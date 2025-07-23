"""
Study buddy matching service
Integrates compatibility engine with CSP solver for optimal partner matching
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from smart_buddy.models.sqlalchemy_models import Profile
from smart_buddy.matching.compatibility_engine import CompatibilityEngine, StudentProfile, CompatibilityScore
from smart_buddy.matching.csp_solver import CSPSolver, StudySession, SchedulingConstraints


class StudyBuddyMatcher:
    """Main service for finding and scheduling study buddy matches"""
    
    def __init__(self, 
                 personality_weight: float = 0.25,
                 study_preferences_weight: float = 0.25,
                 academic_goals_weight: float = 0.25,
                 availability_weight: float = 0.25,
                 constraints: Optional[SchedulingConstraints] = None):
        """
        Initialize the study buddy matcher
        
        Args:
            personality_weight: Weight for personality compatibility
            study_preferences_weight: Weight for study preferences
            academic_goals_weight: Weight for academic goals alignment
            availability_weight: Weight for availability overlap
            constraints: Scheduling constraints for CSP solver
        """
        self.compatibility_engine = CompatibilityEngine(
            personality_weight=personality_weight,
            study_preferences_weight=study_preferences_weight,
            academic_goals_weight=academic_goals_weight,
            availability_weight=availability_weight
        )
        self.csp_solver = CSPSolver(constraints)
    
    def get_student_profiles(self, db: Session, exclude_student_id: Optional[int] = None) -> List[StudentProfile]:
        """Get all student profiles from database"""
        query = db.query(Profile)
        if exclude_student_id:
            query = query.filter(Profile.id != exclude_student_id)
        
        profiles = query.all()
        return [StudentProfile.from_db_profile(profile) for profile in profiles]
    
    def find_matches_for_student(self, 
                                student_id: int, 
                                db: Session,
                                min_score: float = 50.0,
                                max_results: int = 10,
                                include_scheduling: bool = True) -> Dict:
        """
        Find compatible study partners for a specific student
        
        Args:
            student_id: ID of the student looking for matches
            db: Database session
            min_score: Minimum compatibility score threshold
            max_results: Maximum number of matches to return
            include_scheduling: Whether to include scheduling analysis
            
        Returns:
            Dictionary with matches and optional scheduling information
        """
        # Get the student's profile
        student_profile_db = db.query(Profile).filter(Profile.id == student_id).first()
        if not student_profile_db:
            return {"error": "Student not found"}
        
        student_profile = StudentProfile.from_db_profile(student_profile_db)
        
        # Get potential partners (all other students)
        potential_partners = self.get_student_profiles(db, exclude_student_id=student_id)
        
        if not potential_partners:
            return {"matches": [], "message": "No other students found in the system"}
        
        # Find compatible matches
        matches = self.compatibility_engine.find_matches(
            student=student_profile,
            potential_partners=potential_partners,
            min_score=min_score,
            max_results=max_results
        )
        
        result = {
            "student_id": student_id,
            "student_username": student_profile.username,
            "total_potential_partners": len(potential_partners),
            "matches_found": len(matches),
            "matches": [match.to_dict() for match in matches]
        }
        
        # Add scheduling analysis if requested
        if include_scheduling and matches:
            scheduling_analysis = self._analyze_scheduling_feasibility(
                student_profile=student_profile,
                matches=matches,
                db=db
            )
            result["scheduling_analysis"] = scheduling_analysis
        
        return result
    
    def _analyze_scheduling_feasibility(self, 
                                      student_profile: StudentProfile, 
                                      matches: List[CompatibilityScore],
                                      db: Session) -> Dict:
        """Analyze scheduling feasibility for matches"""
        
        # Create availability mapping
        student_availabilities = {student_profile.id: student_profile.availability}
        
        # Add partner availabilities
        partner_ids = [match.partner_id for match in matches]
        partner_profiles = db.query(Profile).filter(Profile.id.in_(partner_ids)).all()
        
        for profile in partner_profiles:
            partner_student_profile = StudentProfile.from_db_profile(profile)
            student_availabilities[profile.id] = partner_student_profile.availability
        
        # Create compatibility pairs for CSP solver
        compatibility_pairs = [
            (student_profile.id, match.partner_id, match.total_score)
            for match in matches
        ]
        
        # Solve scheduling
        proposed_schedule = self.csp_solver.solve_schedule(
            student_availabilities=student_availabilities,
            compatibility_pairs=compatibility_pairs,
            max_sessions_to_schedule=len(matches)
        )
        
        # Validate schedule
        is_valid, violations = self.csp_solver.validate_full_schedule(proposed_schedule)
        
        # Group sessions by partner for summary
        sessions_by_partner = {}
        for session in proposed_schedule:
            partner_id = session.partner2_id if session.partner1_id == student_profile.id else session.partner1_id
            if partner_id not in sessions_by_partner:
                sessions_by_partner[partner_id] = []
            sessions_by_partner[partner_id].append({
                "day": session.schedule_slot.day,
                "time": session.schedule_slot.time,
                "duration_hours": session.duration_hours
            })
        
        return {
            "scheduling_feasible": is_valid,
            "total_sessions_possible": len(proposed_schedule),
            "partners_with_sessions": len(sessions_by_partner),
            "constraint_violations": violations,
            "proposed_sessions": sessions_by_partner
        }
    
    def create_study_group_schedule(self, 
                                  student_ids: List[int], 
                                  db: Session,
                                  optimize: bool = True) -> Dict:
        """
        Create an optimal study schedule for a group of students
        
        Args:
            student_ids: List of student IDs to include in scheduling
            db: Database session
            optimize: Whether to optimize the initial schedule
            
        Returns:
            Dictionary with complete schedule and analysis
        """
        # Get student profiles
        profiles = db.query(Profile).filter(Profile.id.in_(student_ids)).all()
        student_profiles = [StudentProfile.from_db_profile(p) for p in profiles]
        
        if len(student_profiles) < 2:
            return {"error": "At least 2 students required for scheduling"}
        
        # Create availability mapping
        student_availabilities = {
            profile.id: profile.availability 
            for profile in student_profiles
        }
        
        # Generate all possible pairs and their compatibility scores
        compatibility_pairs = []
        for i, student1 in enumerate(student_profiles):
            for student2 in student_profiles[i+1:]:
                score = self.compatibility_engine.compute_compatibility_score(student1, student2)
                compatibility_pairs.append((student1.id, student2.id, score.total_score))
        
        # Solve initial schedule
        initial_schedule = self.csp_solver.solve_schedule(
            student_availabilities=student_availabilities,
            compatibility_pairs=compatibility_pairs
        )
        
        # Optimize if requested
        final_schedule = initial_schedule
        if optimize and initial_schedule:
            final_schedule = self.csp_solver.optimize_schedule(
                initial_schedule=initial_schedule,
                student_availabilities=student_availabilities
            )
        
        # Validate final schedule
        is_valid, violations = self.csp_solver.validate_full_schedule(final_schedule)
        
        # Create detailed schedule summary
        schedule_summary = self._create_schedule_summary(final_schedule, student_profiles)
        
        return {
            "student_ids": student_ids,
            "total_students": len(student_profiles),
            "total_possible_pairs": len(compatibility_pairs),
            "scheduled_sessions": len(final_schedule),
            "schedule_valid": is_valid,
            "constraint_violations": violations,
            "schedule": schedule_summary,
            "optimization_applied": optimize
        }
    
    def _create_schedule_summary(self, 
                               sessions: List[StudySession], 
                               student_profiles: List[StudentProfile]) -> Dict:
        """Create a detailed summary of the schedule"""
        
        # Create student lookup
        student_lookup = {profile.id: profile.username for profile in student_profiles}
        
        # Group sessions by day
        schedule_by_day = {}
        for session in sessions:
            day = session.schedule_slot.day
            if day not in schedule_by_day:
                schedule_by_day[day] = []
            
            schedule_by_day[day].append({
                "time": session.schedule_slot.time,
                "partner1": {
                    "id": session.partner1_id,
                    "username": student_lookup.get(session.partner1_id, "Unknown")
                },
                "partner2": {
                    "id": session.partner2_id,
                    "username": student_lookup.get(session.partner2_id, "Unknown")
                },
                "duration_hours": session.duration_hours
            })
        
        # Sort sessions within each day by time
        time_order = {"Morning": 1, "Afternoon": 2, "Evening": 3}
        for day in schedule_by_day:
            schedule_by_day[day].sort(key=lambda x: time_order.get(x["time"], 4))
        
        # Calculate statistics
        total_study_hours = sum(session.duration_hours for session in sessions)
        
        # Count sessions per student
        student_session_counts = {}
        for session in sessions:
            for student_id in [session.partner1_id, session.partner2_id]:
                student_session_counts[student_id] = student_session_counts.get(student_id, 0) + 1
        
        return {
            "by_day": schedule_by_day,
            "statistics": {
                "total_sessions": len(sessions),
                "total_study_hours": total_study_hours,
                "days_with_sessions": len(schedule_by_day),
                "student_session_counts": {
                    student_lookup.get(student_id, f"Student {student_id}"): count
                    for student_id, count in student_session_counts.items()
                }
            }
        }
    
    def get_compatibility_matrix(self, student_ids: List[int], db: Session) -> Dict:
        """
        Generate a compatibility matrix for a group of students
        
        Args:
            student_ids: List of student IDs to analyze
            db: Database session
            
        Returns:
            Dictionary with compatibility matrix and analysis
        """
        # Get student profiles
        profiles = db.query(Profile).filter(Profile.id.in_(student_ids)).all()
        student_profiles = [StudentProfile.from_db_profile(p) for p in profiles]
        
        if len(student_profiles) < 2:
            return {"error": "At least 2 students required for compatibility analysis"}
        
        # Create compatibility matrix
        matrix = {}
        detailed_scores = {}
        
        for i, student1 in enumerate(student_profiles):
            student1_key = f"{student1.id}_{student1.username}"
            matrix[student1_key] = {}
            detailed_scores[student1_key] = {}
            
            for student2 in student_profiles:
                student2_key = f"{student2.id}_{student2.username}"
                
                if student1.id == student2.id:
                    matrix[student1_key][student2_key] = 100.0  # Perfect self-match
                    detailed_scores[student1_key][student2_key] = {
                        "total_score": 100.0,
                        "note": "Self-match"
                    }
                else:
                    score = self.compatibility_engine.compute_compatibility_score(student1, student2)
                    matrix[student1_key][student2_key] = round(score.total_score, 2)
                    detailed_scores[student1_key][student2_key] = score.to_dict()
        
        # Calculate summary statistics
        all_scores = []
        for student1_key in matrix:
            for student2_key in matrix[student1_key]:
                if student1_key != student2_key:  # Exclude self-matches
                    all_scores.append(matrix[student1_key][student2_key])
        
        summary_stats = {
            "total_pairs": len(all_scores),
            "average_compatibility": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
            "highest_compatibility": max(all_scores) if all_scores else 0,
            "lowest_compatibility": min(all_scores) if all_scores else 0,
            "pairs_above_70": sum(1 for score in all_scores if score >= 70),
            "pairs_above_80": sum(1 for score in all_scores if score >= 80),
            "pairs_above_90": sum(1 for score in all_scores if score >= 90)
        }
        
        return {
            "student_count": len(student_profiles),
            "compatibility_matrix": matrix,
            "detailed_scores": detailed_scores,
            "summary_statistics": summary_stats
        }

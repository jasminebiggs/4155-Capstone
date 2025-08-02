"""
CSP (Constraint Satisfaction Problem) solver for study buddy scheduling
Ensures that matched partners have feasible time slots for study sessions
"""
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum
import itertools


class TimeSlot(Enum):
    """Available time slots"""
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"


class DayOfWeek(Enum):
    """Days of the week"""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


@dataclass
class ScheduleSlot:
    """A specific time slot in the schedule"""
    day: str
    time: str
    
    def __hash__(self):
        return hash((self.day, self.time))
    
    def __eq__(self, other):
        return isinstance(other, ScheduleSlot) and self.day == other.day and self.time == other.time
    
    def __str__(self):
        return f"{self.day} {self.time}"


@dataclass
class StudySession:
    """A scheduled study session between partners"""
    partner1_id: int
    partner2_id: int
    schedule_slot: ScheduleSlot
    duration_hours: float = 2.0  # Default 2-hour sessions
    
    def __str__(self):
        return f"Session: Partners {self.partner1_id}-{self.partner2_id} on {self.schedule_slot}"


class SchedulingConstraints:
    """Constraints for scheduling study sessions"""
    
    def __init__(self):
        self.max_sessions_per_day = 2
        self.max_sessions_per_week = 6
        self.min_break_between_sessions = 1  # Hours
        self.preferred_session_length = 2.0  # Hours
        self.max_partners_per_student = 3
    
    def validate_session(self, session: StudySession, existing_sessions: List[StudySession]) -> bool:
        """Validate if a session can be scheduled given existing sessions"""
        
        # Check daily session limit for both partners
        same_day_sessions = [s for s in existing_sessions 
                           if s.schedule_slot.day == session.schedule_slot.day]
        
        partner1_same_day = sum(1 for s in same_day_sessions 
                              if session.partner1_id in [s.partner1_id, s.partner2_id])
        partner2_same_day = sum(1 for s in same_day_sessions 
                              if session.partner2_id in [s.partner1_id, s.partner2_id])
        
        if partner1_same_day >= self.max_sessions_per_day or partner2_same_day >= self.max_sessions_per_day:
            return False
        
        # Check weekly session limit
        partner1_weekly = sum(1 for s in existing_sessions 
                            if session.partner1_id in [s.partner1_id, s.partner2_id])
        partner2_weekly = sum(1 for s in existing_sessions 
                            if session.partner2_id in [s.partner1_id, s.partner2_id])
        
        if partner1_weekly >= self.max_sessions_per_week or partner2_weekly >= self.max_sessions_per_week:
            return False
        
        # Check maximum partners constraint
        partner1_partners = set()
        partner2_partners = set()
        
        for s in existing_sessions:
            if s.partner1_id == session.partner1_id:
                partner1_partners.add(s.partner2_id)
            elif s.partner2_id == session.partner1_id:
                partner1_partners.add(s.partner1_id)
            
            if s.partner1_id == session.partner2_id:
                partner2_partners.add(s.partner2_id)
            elif s.partner2_id == session.partner2_id:
                partner2_partners.add(s.partner1_id)
        
        # Add current partner
        partner1_partners.add(session.partner2_id)
        partner2_partners.add(session.partner1_id)
        
        if len(partner1_partners) > self.max_partners_per_student or len(partner2_partners) > self.max_partners_per_student:
            return False
        
        return True


class CSPSolver:
    """Constraint Satisfaction Problem solver for study session scheduling"""
    
    def __init__(self, constraints: Optional[SchedulingConstraints] = None):
        self.constraints = constraints or SchedulingConstraints()
    
    def get_available_slots(self, availability: Dict[str, List[str]]) -> Set[ScheduleSlot]:
        """Convert availability dictionary to set of ScheduleSlot objects"""
        slots = set()
        for day, time_slots in availability.items():
            for time_slot in time_slots:
                slots.add(ScheduleSlot(day=day, time=time_slot))
        return slots
    
    def find_common_availability(self, partner1_availability: Dict[str, List[str]], 
                                partner2_availability: Dict[str, List[str]]) -> Set[ScheduleSlot]:
        """Find overlapping availability between two partners"""
        partner1_slots = self.get_available_slots(partner1_availability)
        partner2_slots = self.get_available_slots(partner2_availability)
        
        return partner1_slots.intersection(partner2_slots)
    
    def solve_schedule(self, student_availabilities: Dict[int, Dict[str, List[str]]], 
                      compatibility_pairs: List[Tuple[int, int, float]],
                      max_sessions_to_schedule: int = 20) -> List[StudySession]:
        """
        Solve the scheduling CSP to create optimal study session schedule
        
        Args:
            student_availabilities: Dict mapping student_id -> availability dict
            compatibility_pairs: List of (student1_id, student2_id, compatibility_score) tuples
            max_sessions_to_schedule: Maximum number of sessions to schedule
            
        Returns:
            List of scheduled StudySession objects that satisfy all constraints
        """
        # Sort pairs by compatibility score (descending)
        sorted_pairs = sorted(compatibility_pairs, key=lambda x: x[2], reverse=True)
        
        scheduled_sessions = []
        
        for student1_id, student2_id, score in sorted_pairs:
            if len(scheduled_sessions) >= max_sessions_to_schedule:
                break
            
            # Get availability for both students
            if student1_id not in student_availabilities or student2_id not in student_availabilities:
                continue
            
            availability1 = student_availabilities[student1_id]
            availability2 = student_availabilities[student2_id]
            
            # Find common availability slots
            common_slots = self.find_common_availability(availability1, availability2)
            
            if not common_slots:
                continue  # No common availability
            
            # Try to schedule sessions in common slots
            slots_to_try = list(common_slots)
            # Sort slots by preference (e.g., weekdays first, mornings preferred)
            slots_to_try.sort(key=self._slot_preference_key)
            
            for slot in slots_to_try:
                # Create potential session
                potential_session = StudySession(
                    partner1_id=student1_id,
                    partner2_id=student2_id,
                    schedule_slot=slot
                )
                
                # Check if this session violates any constraints
                if self.constraints.validate_session(potential_session, scheduled_sessions):
                    scheduled_sessions.append(potential_session)
                    break  # Only schedule one session per pair for now
        
        return scheduled_sessions
    
    def _slot_preference_key(self, slot: ScheduleSlot) -> Tuple[int, int]:
        """
        Generate sorting key for slot preferences
        Lower values = higher preference
        """
        # Day preference (weekdays before weekends)
        day_order = {
            'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5,
            'Saturday': 6, 'Sunday': 7
        }
        day_priority = day_order.get(slot.day, 8)
        
        # Time preference (Morning, Afternoon, Evening)
        time_order = {
            'Morning': 1, 'Afternoon': 2, 'Evening': 3
        }
        time_priority = time_order.get(slot.time, 4)
        
        return (day_priority, time_priority)
    
    def validate_full_schedule(self, sessions: List[StudySession]) -> Tuple[bool, List[str]]:
        """
        Validate entire schedule against all constraints
        
        Returns:
            Tuple of (is_valid, list_of_constraint_violations)
        """
        violations = []
        
        # Group sessions by student
        student_sessions = {}
        for session in sessions:
            for student_id in [session.partner1_id, session.partner2_id]:
                if student_id not in student_sessions:
                    student_sessions[student_id] = []
                student_sessions[student_id].append(session)
        
        # Check constraints for each student
        for student_id, student_session_list in student_sessions.items():
            # Check daily session limits
            daily_sessions = {}
            for session in student_session_list:
                day = session.schedule_slot.day
                daily_sessions[day] = daily_sessions.get(day, 0) + 1
            
            for day, count in daily_sessions.items():
                if count > self.constraints.max_sessions_per_day:
                    violations.append(f"Student {student_id} has {count} sessions on {day} (max: {self.constraints.max_sessions_per_day})")
            
            # Check weekly session limit
            if len(student_session_list) > self.constraints.max_sessions_per_week:
                violations.append(f"Student {student_id} has {len(student_session_list)} sessions per week (max: {self.constraints.max_sessions_per_week})")
            
            # Check partner limit
            partners = set()
            for session in student_session_list:
                other_partner = session.partner2_id if session.partner1_id == student_id else session.partner1_id
                partners.add(other_partner)
            
            if len(partners) > self.constraints.max_partners_per_student:
                violations.append(f"Student {student_id} has {len(partners)} different partners (max: {self.constraints.max_partners_per_student})")
        
        return len(violations) == 0, violations
    
    def optimize_schedule(self, initial_schedule: List[StudySession], 
                         student_availabilities: Dict[int, Dict[str, List[str]]]) -> List[StudySession]:
        """
        Optimize an initial schedule by trying to improve slot assignments
        
        Args:
            initial_schedule: Initial schedule to optimize
            student_availabilities: Student availability data
            
        Returns:
            Optimized schedule
        """
        optimized_schedule = initial_schedule.copy()
        
        # Try to move sessions to more preferred time slots
        for i, session in enumerate(optimized_schedule):
            current_slot = session.schedule_slot
            
            # Get common availability for this pair
            availability1 = student_availabilities.get(session.partner1_id, {})
            availability2 = student_availabilities.get(session.partner2_id, {})
            common_slots = self.find_common_availability(availability1, availability2)
            
            # Remove current session temporarily
            temp_schedule = optimized_schedule[:i] + optimized_schedule[i+1:]
            
            # Try better slots
            better_slots = [slot for slot in common_slots 
                          if self._slot_preference_key(slot) < self._slot_preference_key(current_slot)]
            
            for better_slot in better_slots:
                test_session = StudySession(
                    partner1_id=session.partner1_id,
                    partner2_id=session.partner2_id,
                    schedule_slot=better_slot
                )
                
                if self.constraints.validate_session(test_session, temp_schedule):
                    optimized_schedule[i] = test_session
                    break
        
        return optimized_schedule

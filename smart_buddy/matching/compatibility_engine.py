"""
Compatibility scoring engine for study buddy matching
Uses weighted scoring across personality, study preferences, academic goals, and availability
"""
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
from enum import Enum


class PersonalityType(Enum):
    """Personality types for compatibility matching"""
    INTROVERT = "Introvert"
    EXTROVERT = "Extrovert"
    AMBIVERT = "Ambivert"


class StudyStyle(Enum):
    """Study style preferences"""
    GROUP = "Group"
    INDIVIDUAL = "Individual"
    MIXED = "Mixed"


class Environment(Enum):
    """Preferred study environments"""
    QUIET = "Quiet"
    COLLABORATIVE = "Collaborative"
    MIXED = "Mixed"


@dataclass
class StudentProfile:
    """Student profile for matching"""
    id: int
    username: str
    email: str
    personality_type: str
    study_style: str
    preferred_environment: str
    academic_focus_areas: List[str]
    availability: Dict[str, List[str]]  # day -> time_slots
    
    @classmethod
    def from_db_profile(cls, profile):
        """Create StudentProfile from database Profile model"""
        # Parse JSON fields if they're strings
        academic_areas = profile.academic_focus_areas
        if isinstance(academic_areas, str):
            try:
                # Try to parse as JSON first
                academic_areas = json.loads(academic_areas)
                if not isinstance(academic_areas, list):
                    academic_areas = [str(academic_areas)]
            except:
                # If JSON parsing fails, treat as single string
                academic_areas = [academic_areas] if academic_areas.strip() else []
        elif academic_areas is None:
            academic_areas = []
        elif not isinstance(academic_areas, list):
            academic_areas = [str(academic_areas)]
        
        # Ensure all items in the list are strings
        academic_areas = [str(area) for area in academic_areas if area]
        
        personality = profile.personality_traits
        if isinstance(personality, str):
            try:
                personality_data = json.loads(personality)
                if isinstance(personality_data, dict) and 'type' in personality_data:
                    personality = personality_data['type']
                else:
                    personality = str(personality_data)
            except:
                personality = personality
        
        availability = profile.availability or {}
        if isinstance(availability, str):
            try:
                availability = json.loads(availability)
            except:
                availability = {}
        
        return cls(
            id=profile.id,
            username=profile.username,
            email=profile.email,
            personality_type=str(personality),
            study_style=profile.study_style,
            preferred_environment=profile.preferred_environment,
            academic_focus_areas=academic_areas,
            availability=availability
        )


@dataclass
class CompatibilityScore:
    """Compatibility score breakdown"""
    partner_id: int
    partner_username: str
    total_score: float
    personality_score: float
    study_preferences_score: float
    academic_goals_score: float
    availability_score: float
    shared_time_slots: List[Tuple[str, str]]  # (day, time_slot) pairs
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            'partner_id': self.partner_id,
            'partner_username': self.partner_username,
            'total_score': round(self.total_score, 2),
            'personality_score': round(self.personality_score, 2),
            'study_preferences_score': round(self.study_preferences_score, 2),
            'academic_goals_score': round(self.academic_goals_score, 2),
            'availability_score': round(self.availability_score, 2),
            'shared_time_slots': self.shared_time_slots,
            'compatibility_breakdown': {
                'personality': round(self.personality_score, 2),
                'study_preferences': round(self.study_preferences_score, 2),
                'academic_goals': round(self.academic_goals_score, 2),
                'availability': round(self.availability_score, 2)
            }
        }


class CompatibilityEngine:
    """Main compatibility scoring engine"""
    
    def __init__(self, 
                 personality_weight: float = 0.25,
                 study_preferences_weight: float = 0.25,
                 academic_goals_weight: float = 0.25,
                 availability_weight: float = 0.25):
        """
        Initialize compatibility engine with scoring weights
        
        Args:
            personality_weight: Weight for personality compatibility (0-1)
            study_preferences_weight: Weight for study preferences (0-1)
            academic_goals_weight: Weight for academic goals alignment (0-1)
            availability_weight: Weight for availability overlap (0-1)
        """
        # Ensure weights sum to 1.0
        total_weight = personality_weight + study_preferences_weight + academic_goals_weight + availability_weight
        
        self.personality_weight = personality_weight / total_weight
        self.study_preferences_weight = study_preferences_weight / total_weight
        self.academic_goals_weight = academic_goals_weight / total_weight
        self.availability_weight = availability_weight / total_weight
    
    def compute_personality_compatibility(self, student1: StudentProfile, student2: StudentProfile) -> float:
        """
        Compute personality compatibility score (0-100)
        
        Scoring rules:
        - Same personality type: 100
        - Introvert + Extrovert: 70 (can complement each other)
        - Any + Ambivert: 85 (ambivert adapts well)
        """
        p1 = student1.personality_type.upper() if hasattr(student1.personality_type, 'upper') else str(student1.personality_type).upper()
        p2 = student2.personality_type.upper() if hasattr(student2.personality_type, 'upper') else str(student2.personality_type).upper()
        
        if p1 == p2:
            return 100.0
        
        # Handle ambivert compatibility
        if 'AMBIVERT' in [p1, p2]:
            return 85.0
        
        # Introvert + Extrovert can be complementary
        if set([p1, p2]) == {'INTROVERT', 'EXTROVERT'}:
            return 70.0
        
        # Default compatibility for unknown combinations
        return 60.0
    
    def compute_study_preferences_compatibility(self, student1: StudentProfile, student2: StudentProfile) -> float:
        """
        Compute study preferences compatibility score (0-100)
        
        Considers both study style and environment preferences
        """
        style_score = self._compute_study_style_score(student1.study_style, student2.study_style)
        environment_score = self._compute_environment_score(student1.preferred_environment, student2.preferred_environment)
        
        # Average the two components
        return (style_score + environment_score) / 2.0
    
    def _compute_study_style_score(self, style1: str, style2: str) -> float:
        """Compute study style compatibility"""
        s1 = style1.upper() if hasattr(style1, 'upper') else str(style1).upper()
        s2 = style2.upper() if hasattr(style2, 'upper') else str(style2).upper()
        
        if s1 == s2:
            return 100.0
        
        # Mixed style is compatible with both
        if 'MIXED' in [s1, s2]:
            return 85.0
        
        # Group + Individual: moderate compatibility
        if set([s1, s2]) == {'GROUP', 'INDIVIDUAL'}:
            return 60.0
        
        return 70.0
    
    def _compute_environment_score(self, env1: str, env2: str) -> float:
        """Compute environment preference compatibility"""
        e1 = env1.upper() if hasattr(env1, 'upper') else str(env1).upper()
        e2 = env2.upper() if hasattr(env2, 'upper') else str(env2).upper()
        
        if e1 == e2:
            return 100.0
        
        # Mixed environment is adaptable
        if 'MIXED' in [e1, e2]:
            return 85.0
        
        # Quiet + Collaborative: some compatibility
        if set([e1, e2]) == {'QUIET', 'COLLABORATIVE'}:
            return 65.0
        
        return 70.0
    
    def compute_academic_goals_compatibility(self, student1: StudentProfile, student2: StudentProfile) -> float:
        """
        Compute academic goals compatibility score (0-100)
        
        Based on overlap in academic focus areas
        """
        # Ensure academic_focus_areas is a list and convert to strings
        areas1_raw = student1.academic_focus_areas if student1.academic_focus_areas else []
        areas2_raw = student2.academic_focus_areas if student2.academic_focus_areas else []
        
        # Convert all items to strings and filter out empty ones
        areas1 = set()
        for area in areas1_raw:
            if area and str(area).strip():
                areas1.add(str(area).upper().strip())
        
        areas2 = set()
        for area in areas2_raw:
            if area and str(area).strip():
                areas2.add(str(area).upper().strip())
        
        if not areas1 or not areas2:
            return 50.0  # Neutral score if no areas specified
        
        # Calculate Jaccard similarity
        intersection = areas1.intersection(areas2)
        union = areas1.union(areas2)
        
        if not union:
            return 50.0
        
        jaccard_score = len(intersection) / len(union)
        
        # Convert to 0-100 scale with minimum of 30 for any academic overlap
        base_score = 30.0
        variable_score = 70.0 * jaccard_score
        
        return base_score + variable_score
    
    def compute_availability_compatibility(self, student1: StudentProfile, student2: StudentProfile) -> Tuple[float, List[Tuple[str, str]]]:
        """
        Compute availability compatibility score (0-100) and shared time slots
        
        Returns:
            Tuple of (score, shared_time_slots)
        """
        shared_slots = []
        total_slots_student1 = 0
        
        # Count all available slots for student1
        for day, time_slots in student1.availability.items():
            total_slots_student1 += len(time_slots)
        
        if total_slots_student1 == 0:
            return 0.0, []
        
        # Find overlapping availability
        for day, time_slots1 in student1.availability.items():
            if day in student2.availability:
                time_slots2 = student2.availability[day]
                common_slots = set(time_slots1).intersection(set(time_slots2))
                for slot in common_slots:
                    shared_slots.append((day, slot))
        
        # Calculate score based on proportion of shared availability
        shared_count = len(shared_slots)
        
        if shared_count == 0:
            return 0.0, []
        
        # Score based on percentage of overlap plus bonus for absolute number
        overlap_percentage = (shared_count / total_slots_student1) * 100
        
        # Bonus points for having multiple shared slots (up to 20 bonus points)
        bonus = min(20.0, shared_count * 3)
        
        final_score = min(100.0, overlap_percentage + bonus)
        
        return final_score, shared_slots
    
    def compute_compatibility_score(self, student: StudentProfile, potential_partner: StudentProfile) -> CompatibilityScore:
        """
        Compute overall compatibility score between two students
        
        Args:
            student: The student looking for matches
            potential_partner: A potential study partner
            
        Returns:
            CompatibilityScore object with detailed breakdown
        """
        # Compute individual component scores
        personality_score = self.compute_personality_compatibility(student, potential_partner)
        study_preferences_score = self.compute_study_preferences_compatibility(student, potential_partner)
        academic_goals_score = self.compute_academic_goals_compatibility(student, potential_partner)
        availability_score, shared_slots = self.compute_availability_compatibility(student, potential_partner)
        
        # Compute weighted total score
        total_score = (
            personality_score * self.personality_weight +
            study_preferences_score * self.study_preferences_weight +
            academic_goals_score * self.academic_goals_weight +
            availability_score * self.availability_weight
        )
        
        return CompatibilityScore(
            partner_id=potential_partner.id,
            partner_username=potential_partner.username,
            total_score=total_score,
            personality_score=personality_score,
            study_preferences_score=study_preferences_score,
            academic_goals_score=academic_goals_score,
            availability_score=availability_score,
            shared_time_slots=shared_slots
        )
    
    def find_matches(self, student: StudentProfile, potential_partners: List[StudentProfile], 
                    min_score: float = 50.0, max_results: int = 10) -> List[CompatibilityScore]:
        """
        Find compatible study partners for a student
        
        Args:
            student: The student looking for matches
            potential_partners: List of potential study partners
            min_score: Minimum compatibility score threshold (0-100)
            max_results: Maximum number of results to return
            
        Returns:
            List of CompatibilityScore objects sorted by total score (descending)
        """
        compatibility_scores = []
        
        for partner in potential_partners:
            # Skip self-matching
            if partner.id == student.id:
                continue
            
            score = self.compute_compatibility_score(student, partner)
            
            # Only include matches above minimum threshold
            if score.total_score >= min_score:
                compatibility_scores.append(score)
        
        # Sort by total score (descending) and limit results
        compatibility_scores.sort(key=lambda x: x.total_score, reverse=True)
        return compatibility_scores[:max_results]

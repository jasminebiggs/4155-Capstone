"""
API router for study buddy matching functionality
Provides endpoints for finding matches and scheduling study sessions
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from smart_buddy.db import get_db
from smart_buddy.matching.matching_service import StudyBuddyMatcher
from smart_buddy.matching.csp_solver import SchedulingConstraints
from pydantic import BaseModel


router = APIRouter(prefix="/matching", tags=["matching"])


class MatchingRequest(BaseModel):
    """Request model for finding matches"""
    student_id: int
    min_score: float = 50.0
    max_results: int = 10
    include_scheduling: bool = True


class MatchingWeights(BaseModel):
    """Model for customizing matching weights"""
    personality_weight: float = 0.25
    study_preferences_weight: float = 0.25
    academic_goals_weight: float = 0.25
    availability_weight: float = 0.25


class GroupSchedulingRequest(BaseModel):
    """Request model for group scheduling"""
    student_ids: List[int]
    optimize: bool = True
    weights: Optional[MatchingWeights] = None


class ConstraintsRequest(BaseModel):
    """Request model for custom scheduling constraints"""
    max_sessions_per_day: int = 2
    max_sessions_per_week: int = 6
    max_partners_per_student: int = 3


def create_matcher(weights: Optional[MatchingWeights] = None, 
                  constraints: Optional[ConstraintsRequest] = None) -> StudyBuddyMatcher:
    """Create a StudyBuddyMatcher with optional custom weights and constraints"""
    
    # Use default weights if not provided
    if weights is None:
        weights = MatchingWeights()
    
    # Create custom constraints if provided
    scheduling_constraints = None
    if constraints:
        scheduling_constraints = SchedulingConstraints()
        scheduling_constraints.max_sessions_per_day = constraints.max_sessions_per_day
        scheduling_constraints.max_sessions_per_week = constraints.max_sessions_per_week
        scheduling_constraints.max_partners_per_student = constraints.max_partners_per_student
    
    return StudyBuddyMatcher(
        personality_weight=weights.personality_weight,
        study_preferences_weight=weights.study_preferences_weight,
        academic_goals_weight=weights.academic_goals_weight,
        availability_weight=weights.availability_weight,
        constraints=scheduling_constraints
    )


@router.get("/find-matches/{student_id}")
async def find_matches(
    student_id: int,
    min_score: float = Query(50.0, ge=0.0, le=100.0, description="Minimum compatibility score"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    include_scheduling: bool = Query(True, description="Include scheduling analysis"),
    db: Session = Depends(get_db)
):
    """
    Find compatible study partners for a student
    
    Args:
        student_id: ID of the student looking for matches
        min_score: Minimum compatibility score (0-100)
        max_results: Maximum number of matches to return
        include_scheduling: Whether to include scheduling feasibility analysis
        db: Database session
        
    Returns:
        List of compatible partners with scores and optional scheduling info
    """
    try:
        matcher = create_matcher()
        results = matcher.find_matches_for_student(
            student_id=student_id,
            db=db,
            min_score=min_score,
            max_results=max_results,
            include_scheduling=include_scheduling
        )
        
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")


@router.post("/find-matches-custom")
async def find_matches_custom(
    request: MatchingRequest,
    weights: Optional[MatchingWeights] = None,
    constraints: Optional[ConstraintsRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Find matches with custom weights and constraints
    
    Args:
        request: Matching request parameters
        weights: Custom weights for compatibility scoring
        constraints: Custom scheduling constraints
        db: Database session
        
    Returns:
        Compatibility results with custom scoring
    """
    try:
        matcher = create_matcher(weights=weights, constraints=constraints)
        results = matcher.find_matches_for_student(
            student_id=request.student_id,
            db=db,
            min_score=request.min_score,
            max_results=request.max_results,
            include_scheduling=request.include_scheduling
        )
        
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        
        # Include the weights used in the response
        results["weights_used"] = weights.dict() if weights else MatchingWeights().dict()
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")


@router.post("/schedule-group")
async def schedule_group(
    request: GroupSchedulingRequest,
    constraints: Optional[ConstraintsRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Create an optimal study schedule for a group of students
    
    Args:
        request: Group scheduling request
        constraints: Custom scheduling constraints
        db: Database session
        
    Returns:
        Complete study schedule with analysis
    """
    try:
        if len(request.student_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 students required for group scheduling")
        
        matcher = create_matcher(weights=request.weights, constraints=constraints)
        results = matcher.create_study_group_schedule(
            student_ids=request.student_ids,
            db=db,
            optimize=request.optimize
        )
        
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating group schedule: {str(e)}")


@router.post("/compatibility-matrix")
async def get_compatibility_matrix(
    student_ids: List[int],
    weights: Optional[MatchingWeights] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a compatibility matrix for a group of students
    
    Args:
        student_ids: List of student IDs to analyze
        weights: Custom weights for compatibility scoring
        db: Database session
        
    Returns:
        Compatibility matrix with detailed scores
    """
    try:
        if len(student_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 students required for compatibility matrix")
        
        matcher = create_matcher(weights=weights)
        results = matcher.get_compatibility_matrix(student_ids=student_ids, db=db)
        
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        
        # Include the weights used in the response
        results["weights_used"] = weights.dict() if weights else MatchingWeights().dict()
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating compatibility matrix: {str(e)}")


@router.get("/test-matching-system")
async def test_matching_system(db: Session = Depends(get_db)):
    """
    Test endpoint to verify the matching system works with current database
    
    Returns:
        System status and sample matching results
    """
    try:
        from smart_buddy.models.sqlalchemy_models import Profile
        
        # Get all profiles
        profiles = db.query(Profile).all()
        
        if len(profiles) < 2:
            return {
                "status": "insufficient_data",
                "message": "Need at least 2 profiles to test matching",
                "profile_count": len(profiles)
            }
        
        # Test basic matching with first student
        test_student_id = profiles[0].id
        matcher = create_matcher()
        
        test_results = matcher.find_matches_for_student(
            student_id=test_student_id,
            db=db,
            min_score=0.0,  # Include all matches for testing
            max_results=5,
            include_scheduling=True
        )
        
        return {
            "status": "success",
            "message": "Matching system is working correctly",
            "profile_count": len(profiles),
            "test_student_id": test_student_id,
            "test_results": test_results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Matching system test failed: {str(e)}",
            "error_details": str(e)
        }


@router.get("/matching-weights-info")
async def get_matching_weights_info():
    """
    Get information about matching weights and scoring system
    
    Returns:
        Documentation about the matching algorithm
    """
    return {
        "matching_algorithm": {
            "description": "Study buddy compatibility scoring based on 4 weighted factors",
            "factors": {
                "personality": {
                    "weight": 0.25,
                    "description": "Personality type compatibility (Introvert/Extrovert/Ambivert)",
                    "scoring": {
                        "same_type": 100,
                        "ambivert_with_any": 85,
                        "introvert_extrovert": 70,
                        "default": 60
                    }
                },
                "study_preferences": {
                    "weight": 0.25,
                    "description": "Study style and environment preferences",
                    "components": ["study_style", "preferred_environment"],
                    "scoring": {
                        "same_preference": 100,
                        "mixed_with_any": 85,
                        "different": 60-70
                    }
                },
                "academic_goals": {
                    "weight": 0.25,
                    "description": "Overlap in academic focus areas",
                    "scoring": "Jaccard similarity (30-100 scale)"
                },
                "availability": {
                    "weight": 0.25,
                    "description": "Shared available time slots",
                    "scoring": "Percentage overlap + bonus for multiple slots"
                }
            },
            "csp_constraints": {
                "max_sessions_per_day": 2,
                "max_sessions_per_week": 6,
                "max_partners_per_student": 3
            }
        },
        "customization": {
            "weights": "All weights can be customized (must sum to 1.0)",
            "constraints": "Scheduling constraints can be modified",
            "thresholds": "Minimum score thresholds can be set"
        }
    }

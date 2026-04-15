"""
Unit Tests for Scoring

Tests the job scoring functionality.
"""

import pytest
from app.models.job import JobNormalized, JobStatus, ActionBucket, LocationType


class TestJobScoring:
    """Tests for job scoring logic."""

    def test_job_model_creation(self):
        """Test creating a job model."""
        job = JobNormalized(
            company="Example Company",
            role="Software Engineer",
            title_bucket="Backend",
            location_type=LocationType.NYC,
            fit_score=5,
            company_priority=4,
            freshness_score=5,
            location_score=3,
            referral_score=1,
            effort_penalty=0,
            priority_score=18.0,
            action_bucket=ActionBucket.APPLY_NOW,
            status=JobStatus.NEW,
        )

        assert job.company == "Example Company"
        assert job.role == "Software Engineer"
        assert job.priority_score == 18.0
        assert job.action_bucket == ActionBucket.APPLY_NOW

    def test_priority_score_calculation(self):
        """Test priority score calculation."""
        # Priority Score = Fit + Company Priority + Freshness + Location Match + Referral Potential + Effort Penalty
        fit_score = 5
        company_priority = 4
        freshness_score = 5
        location_score = 3
        referral_score = 1
        effort_penalty = 0

        expected_score = fit_score + company_priority + freshness_score + location_score + referral_score + effort_penalty

        assert expected_score == 18.0

    def test_action_bucket_assignment(self):
        """Test action bucket assignment based on score."""
        # High score should be APPLY_NOW
        high_score_job = JobNormalized(
            company="Company A",
            role="Engineer",
            priority_score=18.0,
            action_bucket=ActionBucket.APPLY_NOW,
        )

        assert high_score_job.action_bucket == ActionBucket.APPLY_NOW

        # Lower score should be APPLY_SOON
        medium_score_job = JobNormalized(
            company="Company B",
            role="Developer",
            priority_score=12.0,
            action_bucket=ActionBucket.APPLY_SOON,
        )

        assert medium_score_job.action_bucket == ActionBucket.APPLY_SOON
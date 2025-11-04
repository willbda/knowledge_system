"""
Status Semantics Service - Business Rules for Status Interpretation

Written by Claude Code on 2025-10-30

PURPOSE: Single place for all status semantic logic.
This is where we define what statuses MEAN for workflow.

KEY INSIGHT: The database just stores status IDs.
The meaning lives HERE where it's visible and changeable.

WORKFLOW QUESTIONS WE ACTUALLY CARE ABOUT:
1. Is this task actionable? (can/should I work on it now)
2. When is it due? (already in deadline field)
3. Was it successful? (did we achieve our goal)
4. Does it need follow-up? (what's the next action)
"""

from typing import Literal, Optional
from dataclasses import dataclass
from enum import Enum


# The actual workflow states we care about
class WorkflowState(Enum):
    ACTIONABLE = "actionable"       # Need to work on this
    WAITING = "waiting"              # Waiting for external response
    SUCCESSFUL = "successful"        # Goal achieved (got grant, submitted report)
    UNSUCCESSFUL = "unsuccessful"    # Goal not achieved (denied, withdrawn)
    COMPLETE = "complete"           # Done, no further action
    NEEDS_REVIEW = "needs_review"   # Unclear, needs human judgment


@dataclass
class StatusSemantics:
    """What a status means for workflow"""
    workflow_state: WorkflowState
    is_actionable: bool
    is_terminal: bool              # No more work needed
    needs_follow_up: bool
    description: str


class StatusSemanticsService:
    """
    THE source of truth for what statuses mean.

    This is where business rules live. When colleagues need to change
    what a status means, they come HERE, not to the database.
    """

    def get_semantics(
        self,
        status_id: int,
        task_type: Literal["LOI", "Proposal", "Report", "Reminder"]
    ) -> StatusSemantics:
        """
        Given a status ID and task type, return what it means for workflow.

        Status IDs come from the raw_statuses table (auto-increment).
        The actual text doesn't matter - we map by ID.
        """

        # LOI-specific semantics
        if task_type == "LOI":
            return self._loi_semantics(status_id)

        # Proposal-specific semantics
        elif task_type == "Proposal":
            return self._proposal_semantics(status_id)

        # Report-specific semantics
        elif task_type == "Report":
            return self._report_semantics(status_id)

        # Reminder/Other
        else:
            return self._default_semantics(status_id)

    def _loi_semantics(self, status_id: int) -> StatusSemantics:
        """
        LOI workflow semantics.

        Map status IDs to workflow meaning for Letters of Intent.
        These mappings are based on Book2.csv patterns.
        """

        # Based on your Book2.csv, assuming these IDs:
        # 1: "1. Awarded" → For LOI means invited to apply
        # 2: "2. Application Submitted" → Doesn't apply to LOI
        # 3: "3. LOI Submitted" → Waiting for response
        # 4: "4. Draft in Progress" → Actively working
        # 5: "5. Planned" → Future work
        # 6: "6. Research" → Investigating opportunity
        # 8: "8. Denied" → Not invited to apply
        # 10-11: Various forms of "can't apply"

        match status_id:
            case 1:  # "Awarded" for LOI = invited
                return StatusSemantics(
                    workflow_state=WorkflowState.SUCCESSFUL,
                    is_actionable=True,  # Create proposal!
                    is_terminal=False,
                    needs_follow_up=True,
                    description="Invited to submit full proposal"
                )

            case 3:  # "LOI Submitted"
                return StatusSemantics(
                    workflow_state=WorkflowState.WAITING,
                    is_actionable=False,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Waiting for invitation decision"
                )

            case 4:  # "Draft in Progress"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Actively drafting LOI"
                )

            case 5:  # "Planned"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Planned for future submission"
                )

            case 6:  # "Research"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Researching opportunity"
                )

            case 8:  # "Denied"
                return StatusSemantics(
                    workflow_state=WorkflowState.UNSUCCESSFUL,
                    is_actionable=False,
                    is_terminal=True,
                    needs_follow_up=False,
                    description="Not invited to apply"
                )

            case 10 | 11:  # "Withdrawn", "Ineligible", etc.
                return StatusSemantics(
                    workflow_state=WorkflowState.COMPLETE,
                    is_actionable=False,
                    is_terminal=True,
                    needs_follow_up=False,
                    description="Cannot or will not apply"
                )

            case _:
                return StatusSemantics(
                    workflow_state=WorkflowState.NEEDS_REVIEW,
                    is_actionable=False,
                    is_terminal=False,
                    needs_follow_up=True,
                    description="Unknown status - needs review"
                )

    def _proposal_semantics(self, status_id: int) -> StatusSemantics:
        """
        Proposal workflow semantics.

        Map status IDs to workflow meaning for full grant proposals.
        """

        match status_id:
            case 1:  # "Awarded" for Proposal = got the grant!
                return StatusSemantics(
                    workflow_state=WorkflowState.SUCCESSFUL,
                    is_actionable=True,  # Need to create reports
                    is_terminal=False,
                    needs_follow_up=True,
                    description="Grant awarded - schedule reports"
                )

            case 2:  # "Application Submitted"
                return StatusSemantics(
                    workflow_state=WorkflowState.WAITING,
                    is_actionable=False,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Waiting for funding decision"
                )

            case 4:  # "Draft in Progress"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Actively drafting proposal"
                )

            case 7:  # "Awarded-closed"
                return StatusSemantics(
                    workflow_state=WorkflowState.COMPLETE,
                    is_actionable=False,
                    is_terminal=True,
                    needs_follow_up=False,
                    description="Grant complete and closed"
                )

            case 8:  # "Denied"
                return StatusSemantics(
                    workflow_state=WorkflowState.UNSUCCESSFUL,
                    is_actionable=True,  # Maybe request feedback
                    is_terminal=True,
                    needs_follow_up=True,
                    description="Proposal denied - consider feedback"
                )

            case 9:  # "On Hold"
                return StatusSemantics(
                    workflow_state=WorkflowState.WAITING,
                    is_actionable=False,
                    is_terminal=False,
                    needs_follow_up=True,
                    description="On hold - monitor for updates"
                )

            case _:
                return self._default_semantics(status_id)

    def _report_semantics(self, status_id: int) -> StatusSemantics:
        """
        Report workflow semantics.

        Reports have simpler semantics - either working on it or submitted.
        """

        match status_id:
            case 4:  # "Draft in Progress"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Drafting report"
                )

            case 7:  # "Report Submitted"
                return StatusSemantics(
                    workflow_state=WorkflowState.COMPLETE,
                    is_actionable=False,
                    is_terminal=True,
                    needs_follow_up=False,
                    description="Report submitted - complete"
                )

            case 5:  # "Planned"
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=False,  # Not due yet
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Report planned for future"
                )

            case _:
                return StatusSemantics(
                    workflow_state=WorkflowState.ACTIONABLE,
                    is_actionable=True,
                    is_terminal=False,
                    needs_follow_up=False,
                    description="Report needs attention"
                )

    def _default_semantics(self, status_id: int) -> StatusSemantics:
        """Default semantics for unknown combinations"""

        # Safe defaults that trigger review
        return StatusSemantics(
            workflow_state=WorkflowState.NEEDS_REVIEW,
            is_actionable=False,
            is_terminal=False,
            needs_follow_up=True,
            description=f"Status {status_id} needs semantic mapping"
        )


# Convenience functions for common queries
def is_actionable(status_id: int, task_type: str) -> bool:
    """Can/should we work on this task now?"""
    service = StatusSemanticsService()
    semantics = service.get_semantics(status_id, task_type)
    return semantics.is_actionable


def was_successful(status_id: int, task_type: str) -> bool:
    """Did this task achieve its goal?"""
    service = StatusSemanticsService()
    semantics = service.get_semantics(status_id, task_type)
    return semantics.workflow_state == WorkflowState.SUCCESSFUL


def needs_follow_up(status_id: int, task_type: str) -> bool:
    """Does this task need follow-up action?"""
    service = StatusSemanticsService()
    semantics = service.get_semantics(status_id, task_type)
    return semantics.needs_follow_up


def get_actionable_tasks(tasks: list) -> list:
    """Filter to tasks that need work now"""
    service = StatusSemanticsService()
    return [
        task for task in tasks
        if service.get_semantics(task.status_id, task.task_type).is_actionable
    ]
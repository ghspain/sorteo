## 7. State Diagram - Raffle Session Lifecycle

This enhanced state diagram illustrates the complete lifecycle of a raffle session with error states, validations, and detailed transitions.

```mermaid
stateDiagram-v2
    [*] --> Initialized: Create new session

    Initialized --> ValidationFailed: Invalid configuration
    ValidationFailed --> [*]: Abort session

    Initialized --> ParticipantsLoading: Import participants
    ParticipantsLoading --> DataValidationError: Invalid participant data
    DataValidationError --> ParticipantsLoading: Retry with fixed data

    ParticipantsLoading --> ParticipantsLoaded: Participants validated

    ParticipantsLoaded --> ConfiguringRounds: Configure rounds
    ConfiguringRounds --> RoundsConfigured: All rounds configured

    note right of RoundsConfigured
        Session ready for drawing
    end note

    RoundsConfigured --> RoundExecution: Start first round
    RoundExecution --> RoundCompleted: Winners drawn

    RoundCompleted --> RoundExecution: Execute next round
    RoundCompleted --> SessionCompleted: All rounds completed

    RoundExecution --> RoundExecutionFailed: Drawing error
    RoundExecutionFailed --> RoundExecution: Retry round
    RoundExecutionFailed --> SessionPaused: Pause for investigation

    SessionPaused --> RoundExecution: Resume execution
    SessionPaused --> SessionCompleted: Force completion

    SessionCompleted --> ResultsExported: Export results
    ResultsExported --> [*]: End session

    state RoundExecution {
        [*] --> ParticipantSelection: Filter eligible participants
        ParticipantSelection --> WinnerSelection: Apply random selection
        WinnerSelection --> ResultsRecording: Record winners
        ResultsRecording --> EventPublication: Publish winner events
        EventPublication --> [*]: Round execution complete

        WinnerSelection --> SelectionValidation: Validate winners
        SelectionValidation --> WinnerSelection: Selection invalid
        SelectionValidation --> ResultsRecording: Selection valid
    }

    state SessionCompleted {
        [*] --> ResultsCompilation: Compile all results
        ResultsCompilation --> StatisticsGeneration: Generate statistics
        StatisticsGeneration --> FinalEventPublication: Publish completion event
        FinalEventPublication --> [*]: Ready for export
    }
```

This improved state diagram provides:

1. **Error states**: Shows what happens when things go wrong
2. **Validation steps**: Includes validation states for data integrity
3. **Compound states**: Uses nested states to show sub-processes (Round Execution and Session Completed)
4. **Notes**: Adds explanatory notes for key states
5. **Recovery paths**: Shows how to recover from failures
6. **Completion states**: Clearly indicates terminal states and paths
7. **Pause/resume capability**: Shows session management options
8. **Data flow implications**: State transitions imply data transformations

## 6. Sequence Diagram - Raffle Round Execution

This diagram illustrates the detailed sequence of interactions during a raffle round execution, showing the clear separation of concerns between the presentation, application, domain, and infrastructure layers.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as CLI Interface
    participant RaffleService as RaffleService
    participant DrawService as DrawService
    participant SessionService as SessionService
    participant DomainModels as Domain Models
    participant EventPublisher as Event Publisher
    participant LoggingService as Logging Service
    participant NotificationService as Notification Service

    %% Command phase - User initiates the action
    User ->> CLI: Execute raffle round
    CLI ->> RaffleService: execute_round(round_id, session_id)

    %% Retrieve current session state
    RaffleService ->> SessionService: get_session(session_id)
    SessionService -->> RaffleService: session

    %% Retrieve round configuration
    RaffleService ->> SessionService: get_round(round_id)
    SessionService -->> RaffleService: round

    %% Pre-execution validation
    RaffleService ->> RaffleService: validate_can_execute_round(round, session)

    %% Core domain logic - winner selection
    RaffleService ->> DrawService: draw_winners(eligible_participants, num_winners, exclude_emails)

    %% Selection algorithm with randomization
    DrawService ->> DrawService: randomize_participants()
    DrawService ->> DrawService: apply_exclusion_rules()
    DrawService ->> DrawService: select_winners()
    DrawService -->> RaffleService: winners

    %% Update domain model
    RaffleService ->> DomainModels: create_draw_result(round_id, winners, timestamp)
    DomainModels -->> RaffleService: draw_result

    %% Persist results
    RaffleService ->> SessionService: record_winners(round_id, winners)
    SessionService -->> RaffleService: updated_session

    %% Event publication (domain events)
    RaffleService ->> EventPublisher: publish(WinnersSelectedEvent)

    %% Event handling
    par Event Handlers
        EventPublisher ->> LoggingService: handle_event(WinnersSelectedEvent)
        LoggingService -->> EventPublisher: acknowledged
    and
        EventPublisher ->> NotificationService: handle_event(WinnersSelectedEvent)
        NotificationService -->> EventPublisher: acknowledged
    end

    EventPublisher -->> RaffleService: events_processed

    %% Return results to presentation layer
    RaffleService -->> CLI: draw_results

    %% Present results to user
    CLI ->> CLI: format_winner_display(draw_results)
    CLI -->> User: Display winners with prize information
```

This improved sequence diagram provides:

1. **Autonumbering**: Steps are automatically numbered for easier reference
2. **More detailed interactions**: Shows validation and processing steps
3. **Parallel processing**: Illustrates how events are handled in parallel
4. **Clear layer separation**: Shows distinct interactions between presentation, application, domain, and infrastructure
5. **Domain events**: Explicitly shows event publication and subscription
6. **Error handling**: Implicit validation steps before core logic
7. **User feedback**: Shows how results are formatted before presentation

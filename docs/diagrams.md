# Raffle Project Documentation Diagrams

## 1. Domain Model Diagram

This diagram illustrates the core entities, value objects, and their relationships in the domain-driven design approach.

```mermaid
classDiagram
    %% Core Entities with improved styling
    class Participant {
        <<Entity>>
        +Email email
        +PersonName name
        +CheckInDate checked_in_at
        +from_dict(data)
        +to_dict()
        +full_name()
        +is_checked_in()
    }

    class Prize {
        <<Entity>>
        +PrizeId prize_id
        +PrizeName name
        +String description
        +create(id, name, description)
    }

    class Round {
        <<Entity>>
        +RoundId round_id
        +String name
        +int num_winners
        +List~Prize~ prizes
        +create_new(round_id, name, num_winners)
        +add_prize(prize)
        +to_dict()
    }

    class DrawResult {
        <<Entity>>
        +int round_id
        +List~Participant~ winners
        +Datetime timestamp
        +to_dict()
    }

    class RaffleSession {
        <<Aggregate Root>>
        +SessionId id
        +List~Participant~ participants
        +List~Round~ rounds
        +List~Email~ all_winners
        +Dict~int, List~Participant~~ drawn_winners
        +create_new()
        +add_participant(participant)
        +add_round(round)
        +record_winners(round_id, winners)
        +is_previous_winner(email)
    }

    %% Value Objects with improved styling
    class ValueObject {
        <<abstract>>
        +T value
        +equals(other)
    }

    class Email {
        <<Value Object>>
        +String value
        +is_valid_email(email)
        +validate()
    }

    class PersonName {
        <<Value Object>>
        +String first_name
        +String last_name
        +full_name()
        +validate()
    }

    class CheckInDate {
        <<Value Object>>
        +String value
        +Optional~Datetime~ _parsed_datetime
        +parsed_datetime()
        +is_checked_in()
        +validate()
    }

    class SessionId {
        <<Value Object>>
        +String value
        +generate()
        +validate()
    }

    class RoundId {
        <<Value Object>>
        +int value
        +validate()
    }

    class PrizeId {
        <<Value Object>>
        +int value
        +validate()
    }

    class PrizeName {
        <<Value Object>>
        +String value
        +validate()
    }

    %% Domain Events for completeness
    class DomainEvent {
        <<Domain Event>>
        +String event_id
        +Datetime timestamp
        +event_type()
    }

    class WinnerSelectedEvent {
        <<Domain Event>>
        +String round_id
        +List~Participant~ winners
        +to_dict()
    }

    %% Relationships
    ValueObject <|-- Email
    ValueObject <|-- PersonName
    ValueObject <|-- CheckInDate
    ValueObject <|-- SessionId
    ValueObject <|-- RoundId
    ValueObject <|-- PrizeId
    ValueObject <|-- PrizeName

    DomainEvent <|-- WinnerSelectedEvent

    Participant --* Email : contains
    Participant --* PersonName : contains
    Participant --* CheckInDate : contains

    RaffleSession --* SessionId : identified by
    RaffleSession o-- "0..*" Participant : contains
    RaffleSession o-- "0..*" Round : contains
    RaffleSession o-- "0..*" DrawResult : records

    Round --* RoundId : identified by
    Round o-- "0..*" Prize : contains

    Prize --* PrizeId : identified by
    Prize --* PrizeName : contains

    DrawResult --o RoundId : references
    DrawResult o-- "1..*" Participant : includes

    %% Add colors for better visualization
    classDef entity fill:#f9f,stroke:#333,stroke-width:2px
    classDef valueObject fill:#bbf,stroke:#33c,stroke-width:1px
    classDef aggregateRoot fill:#fbb,stroke:#c33,stroke-width:3px
    classDef domainEvent fill:#bfb,stroke:#3c3,stroke-width:1px

    class Participant,Prize,Round,DrawResult entity
    class Email,PersonName,CheckInDate,SessionId,RoundId,PrizeId,PrizeName valueObject
    class RaffleSession aggregateRoot
    class DomainEvent,WinnerSelectedEvent domainEvent
```

**Legend:**

- **Aggregate Root**: Main entity that ensures consistency boundaries
- **Entity**: Object with an identity that persists over time
- **Value Object**: Immutable object defined only by its attributes
- **Domain Event**: Something significant that occurred in the domain

## 2. Architecture Diagram

This diagram illustrates the layered architecture pattern with clear separation of concerns, following SOLID principles and clean architecture concepts.

```mermaid
graph TD
    %% Layers with better organization
    subgraph External["External Systems"]
        CSV[CSV Files]
        CLI[Command Line]
    end

    subgraph Presentation["Presentation Layer"]
        direction LR
        UI[UI Components]
        StateManager[Session State Manager]
        style UI fill:#ffedcc,stroke:#ff9900
        style StateManager fill:#ffedcc,stroke:#ff9900
    end

    subgraph Application["Application Layer"]
        direction LR
        RaffleService[Raffle Service]
        ParticipantService[Participant Service]
        DrawService[Draw Service]
        SessionService[Session Service]
        style RaffleService fill:#e6ffcc,stroke:#00cc00
        style ParticipantService fill:#e6ffcc,stroke:#00cc00
        style DrawService fill:#e6ffcc,stroke:#00cc00
        style SessionService fill:#e6ffcc,stroke:#00cc00
    end

    subgraph Domain["Domain Layer"]
        direction TB
        Entities[Entities & Aggregates]
        ValueObjects[Value Objects]
        DomainEvents[Domain Events]
        DomainServices[Domain Services]
        style Entities fill:#cce6ff,stroke:#0066cc
        style ValueObjects fill:#cce6ff,stroke:#0066cc
        style DomainEvents fill:#cce6ff,stroke:#0066cc
        style DomainServices fill:#cce6ff,stroke:#0066cc
    end

    subgraph Infrastructure["Infrastructure Layer"]
        direction LR
        CSVRepo[CSV Repository]
        Logging[Logging Service]
        ErrorHandling[Error Handling]
        i18n[i18n Service]
        GDPR[GDPR Compliance]
        style CSVRepo fill:#e6ccff,stroke:#6600cc
        style Logging fill:#e6ccff,stroke:#6600cc
        style ErrorHandling fill:#e6ccff,stroke:#6600cc
        style i18n fill:#e6ccff,stroke:#6600cc
        style GDPR fill:#e6ccff,stroke:#6600cc
    end

    %% Relationships with dependency direction following clean architecture
    External --> Presentation
    Presentation --> Application
    Application --> Domain
    Infrastructure --> Domain
    Infrastructure --> Application

    %% Specific component relationships
    CSV --> CSVRepo
    CLI --> UI
    UI --> StateManager
    StateManager --> Application

    %% Add notes for clarity
    classDef note fill:#ffffcc,stroke:#cccc00,stroke-width:1px
    class Note1,Note2,Note3 note

    Note1["Dependencies flow inward toward Domain"]
    Note2["Domain has no dependencies on outer layers"]
    Note3["Infrastructure depends on abstractions, not concrete implementations"]

    Note1 -.- Domain
    Note2 -.- Domain
    Note3 -.- Infrastructure
```

**Legend:**

- **Presentation Layer**: User interface components
- **Application Layer**: Application services that orchestrate domain objects
- **Domain Layer**: Core business logic and rules
- **Infrastructure Layer**: Technical capabilities and external systems integration

## 3. Flow Diagram - Raffle Process

This diagram shows the comprehensive flow of executing a raffle, with improved organization and additional details.

```mermaid
flowchart TD
    %% Style definitions for better visualization
    classDef start fill:#ccffcc,stroke:#009900,stroke-width:2px
    classDef end fill:#ffcccc,stroke:#990000,stroke-width:2px
    classDef process fill:#e6f2ff,stroke:#0066cc,stroke-width:1px
    classDef decision fill:#fff2cc,stroke:#ffcc00,stroke-width:1px
    classDef dataStore fill:#e6ccff,stroke:#6600cc,stroke-width:1px
    classDef domainEvent fill:#ccffff,stroke:#00cccc,stroke-width:1px

    %% Start and initialization
    Start([Start]) --> LoadParticipantsProcess
    LoadParticipantsProcess[/"Load Participants Process"/] --> LoadParticipants[Load Participants from CSV]
    LoadParticipants --> ValidateParticipants{Validate Each\nParticipant}
    ValidateParticipants -->|Valid| FilterCheckedIn{Filter only\nchecked-in?}
    ValidateParticipants -->|Invalid| HandleInvalidEntries[Log Invalid Entries]
    HandleInvalidEntries --> FilterCheckedIn

    %% Filtering process
    FilterCheckedIn -->|Yes| FilterParticipants[Filter checked-in participants]
    FilterCheckedIn -->|No| ConfigureRoundProcess
    FilterParticipants --> ConfigureRoundProcess

    %% Round configuration
    ConfigureRoundProcess[/"Configure Round Process"/] --> SetupRound[Set Round Name, Number of Winners]
    SetupRound --> AddPrizes[Add Prizes to Round]
    AddPrizes --> ValidateRoundConfig{Validate Round\nConfiguration}
    ValidateRoundConfig -->|Valid| PublishRoundCreatedEvent
    ValidateRoundConfig -->|Invalid| FixRoundConfig[Fix Configuration Issues]
    FixRoundConfig --> ValidateRoundConfig

    %% Round execution preparation
    PublishRoundCreatedEvent[Publish Round Created Event] --> ExecuteRoundProcess
    ExecuteRoundProcess[/"Execute Round Process"/] --> ExcludePreviousWinners[Exclude Previous Winners]
    ExcludePreviousWinners --> CheckEligibleCount{Enough Eligible\nParticipants?}
    CheckEligibleCount -->|Yes| SelectWinners[Randomly Select Winners]
    CheckEligibleCount -->|No| NotEnoughParticipants[Handle Not Enough Participants]
    NotEnoughParticipants --> ConfigureRoundProcess

    %% Winner selection and post-processing
    SelectWinners --> PublishWinnerEvent[Publish Winner Selected Event]
    PublishWinnerEvent --> DisplayWinners[Display Winners]

    %% Results handling
    DisplayWinners --> SaveResults[Save Results to Session]
    SaveResults --> RecordWinnersInDB[(Record Winners in Database)]
    RecordWinnersInDB --> Continue{Another Round?}
    Continue -->|Yes| ConfigureRoundProcess
    Continue -->|No| FinalizeProcess[/"Finalize Process"/]
    FinalizeProcess --> PublishSessionCompleted[Publish Session Completed Event]
    PublishSessionCompleted --> GenerateReport[Generate Final Report]
    GenerateReport --> End([End])

    %% Apply styles
    class Start start
    class End end
    class LoadParticipants,FilterParticipants,SetupRound,AddPrizes,ExcludePreviousWinners,SelectWinners,DisplayWinners,SaveResults,GenerateReport process
    class FilterCheckedIn,ValidateParticipants,ValidateRoundConfig,CheckEligibleCount,Continue decision
    class RecordWinnersInDB dataStore
    class PublishRoundCreatedEvent,PublishWinnerEvent,PublishSessionCompleted domainEvent
```

**Legend:**

- **Process**: Standard operations in the flow
- **Decision**: Points where flow branches based on conditions
- **Data Store**: Persistence operations
- **Domain Event**: Events published to notify other parts of the system

## 4. Component Diagram

This diagram shows how the different components interact within the system, following the SOLID principles and highlighting dependencies.

```mermaid
flowchart LR
    %% Style definitions
    classDef interface fill:#e6f2ff,stroke:#0066cc,stroke-width:1px,stroke-dasharray: 5 5
    classDef component fill:#ccffcc,stroke:#009900,stroke-width:1px
    classDef service fill:#ffe6cc,stroke:#ff9900,stroke-width:1px
    classDef infrastructure fill:#e6ccff,stroke:#6600cc,stroke-width:1px

    %% Interfaces (following Dependency Inversion Principle)
    IRaffleService([IRaffleService]):::interface
    IParticipantService([IParticipantService]):::interface
    IDrawService([IDrawService]):::interface
    ISessionService([ISessionService]):::interface
    ICSVRepository([ICSVRepository]):::interface
    IEventPublisher([IEventPublisher]):::interface
    IEventSubscriber([IEventSubscriber]):::interface
    ILogger([ILogger]):::interface
    IErrorHandler([IErrorHandler]):::interface
    Ii18nService([Ii18nService]):::interface

    %% Main components
    CLI[CLI Interface]:::component
    RaffleService[Raffle Service]:::service
    ParticipantService[Participant Service]:::service
    DrawService[Draw Service]:::service
    SessionService[Session Service]:::service
    CSVRepo[CSV Repository]:::infrastructure
    EventPublisher[Domain Event Publisher]:::infrastructure
    EventSubscribers[Domain Event Subscribers]:::infrastructure
    Logger[Logging Service]:::infrastructure
    ErrorHandler[Error Handler]:::infrastructure
    i18nService[i18n Service]:::infrastructure

    %% Relationships - showing dependency on interfaces (not implementations)
    CLI --> IRaffleService
    CLI --> IParticipantService
    CLI --> Ii18nService

    IRaffleService --- RaffleService
    IParticipantService --- ParticipantService
    IDrawService --- DrawService
    ISessionService --- SessionService
    ICSVRepository --- CSVRepo
    IEventPublisher --- EventPublisher
    IEventSubscriber --- EventSubscribers
    ILogger --- Logger
    IErrorHandler --- ErrorHandler
    Ii18nService --- i18nService

    RaffleService --> IDrawService
    RaffleService --> ISessionService
    RaffleService --> IEventPublisher
    RaffleService --> ILogger
    RaffleService --> IErrorHandler

    ParticipantService --> ICSVRepository
    ParticipantService --> ILogger
    ParticipantService --> IErrorHandler

    DrawService --> IEventPublisher
    DrawService --> ILogger
    DrawService --> IErrorHandler

    EventPublisher --> IEventSubscriber

    %% Subgraph for organizing components
    subgraph ApplicationServices["Application Services"]
        RaffleService
        ParticipantService
        DrawService
        SessionService
    end

    subgraph InfrastructureServices["Infrastructure Services"]
        CSVRepo
        EventPublisher
        EventSubscribers
        Logger
        ErrorHandler
        i18nService
    end

    subgraph InterfaceLayer["Interface Layer"]
        CLI
    end
```

**Legend:**

- **Interfaces**: Abstractions that components depend on (dotted borders)
- **Component**: UI interface components
- **Service**: Application services that implement business logic
- **Infrastructure**: Technical capabilities and external integrations

## 5. Sequence Diagram - Participant Import Process

This diagram shows an enhanced view of the participant import process with added validation and error handling.

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant ParticipantService
    participant CSVRepo
    participant Validator
    participant DomainModel
    participant EventPublisher
    participant Logger

    %% Add activation boxes for better visualization of active components
    activate User
    User ->> CLI: Import participants from CSV
    activate CLI

    %% Begin import process
    CLI ->> ParticipantService: process_participants_file(file_path, checked_in_only)
    activate ParticipantService

    %% File validation
    ParticipantService ->> ParticipantService: validate_file_format(file_path)
    ParticipantService ->> CSVRepo: load_participants(file_path)
    activate CSVRepo
    CSVRepo -->> ParticipantService: raw_participant_data
    deactivate CSVRepo

    %% Participant processing with detailed error handling
    ParticipantService ->> Logger: log_info("Processing participants")
    activate Logger
    deactivate Logger

    loop For each participant record
        ParticipantService ->> Validator: validate_email(email)
        activate Validator
        Validator -->> ParticipantService: validation_result
        deactivate Validator

        alt Email is valid
            ParticipantService ->> Validator: validate_name(name)
            activate Validator
            Validator -->> ParticipantService: name_validation_result
            deactivate Validator

            alt Name is valid
                ParticipantService ->> DomainModel: create Participant(email, name, check_in)
                activate DomainModel
                DomainModel -->> ParticipantService: participant_object
                deactivate DomainModel

                %% Record successful participant creation
                ParticipantService ->> EventPublisher: publish(ParticipantImported)
                activate EventPublisher
                EventPublisher -->> ParticipantService: event_published
                deactivate EventPublisher
            else Name is invalid
                ParticipantService ->> Logger: log_warning("Invalid name format")
                activate Logger
                deactivate Logger
            end
        else Email is invalid
            ParticipantService ->> Logger: log_warning("Invalid email format")
            activate Logger
            deactivate Logger
        end
    end

    %% Apply filtering if needed
    alt checked_in_only is True
        ParticipantService ->> ParticipantService: filter_checked_in_participants()
    end

    %% Finalize import
    ParticipantService ->> Logger: log_info("Import completed")
    activate Logger
    deactivate Logger
    ParticipantService -->> CLI: list of valid participants
    deactivate ParticipantService

    %% Display results
    CLI -->> User: Display import results (valid/invalid counts)
    deactivate CLI
    deactivate User
```

**Note:** This sequence diagram includes additional validation steps, error handling, and event publishing that reflect a robust implementation.

## 6. Sequence Diagram - Raffle Round Execution

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant RaffleService
    participant DrawService
    participant SessionService
    participant EventPublisher
    participant EventSubscribers

    User ->> CLI: Execute raffle round
    CLI ->> RaffleService: execute_round(round_id, session)

    RaffleService ->> SessionService: get_round(round_id)
    SessionService -->> RaffleService: round

    RaffleService ->> DrawService: draw_winners(participants, num_winners, exclude_emails)
    DrawService ->> DrawService: Select random winners
    DrawService -->> RaffleService: winners

    RaffleService ->> SessionService: record_winners(round_id, winners)
    SessionService -->> RaffleService: updated session

    RaffleService ->> EventPublisher: publish(WinnersSelectedEvent)
    EventPublisher ->> EventSubscribers: handle_event(WinnersSelectedEvent)
    EventSubscribers -->> EventPublisher: event handled

    RaffleService -->> CLI: draw results
    CLI -->> User: Display winners
```

## 7. State Diagram - Raffle Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: Create new session
    Created --> ParticipantsLoaded: Import participants
    ParticipantsLoaded --> RoundsConfigured: Configure rounds
    RoundsConfigured --> FirstRoundCompleted: Execute first round
    FirstRoundCompleted --> MoreRoundsCompleted: Execute additional rounds
    MoreRoundsCompleted --> MoreRoundsCompleted: Execute additional rounds
    MoreRoundsCompleted --> SessionCompleted: All rounds completed
    SessionCompleted --> [*]: End session

    state FirstRoundCompleted {
        [*] --> SelectWinners
        SelectWinners --> RecordWinners
        RecordWinners --> PublishResults
        PublishResults --> [*]
    }
```

## 8. Deployment Diagram

```mermaid
flowchart TD
    %% Main components
    App[Raffle Application]
    PythonRuntime[Python Runtime]
    AppDependencies[Application Dependencies]
    DataVolume[Data Volume]
    LogsVolume[Logs Volume]
    UserCLI[Command Line Interface]

    %% Container subgraph
    subgraph DockerContainer["Docker Container"]
        App
        PythonRuntime
        AppDependencies
    end

    %% Volume mounts subgraph
    subgraph VolumeMounts["Volume Mounts"]
        DataVolume
        LogsVolume
    end
    class VolumeMounts volume
    class UserInteraction user
```

```mermaid
flowchart TD
    %% Main components
    App[Raffle Application]
    PythonRuntime[Python Runtime]
    AppDependencies[Application Dependencies]
    DataVolume[Data Volume]
    LogsVolume[Logs Volume]
    UserCLI[Command Line Interface]

    %% Container subgraph
    subgraph DockerContainer["Docker Container"]
        App
        PythonRuntime
        AppDependencies
    end

    %% Volume mounts subgraph
    subgraph VolumeMounts["Volume Mounts"]
        DataVolume
        LogsVolume
    end

    %% User interaction subgraph
    subgraph UserInteraction["User Interaction"]
        UserCLI
    end

    %% Relationships with proper syntax
    App --> PythonRuntime
    App --> AppDependencies
    App --> DataVolume
    App --> LogsVolume
    UserCLI --> App

    %% Add labels
    App -- "runs on" --> PythonRuntime
    App -- "uses" --> AppDependencies
    App -- "reads/writes data" --> DataVolume
    App -- "writes logs" --> LogsVolume
    UserCLI -- "interacts with" --> App

    %% Styling
    classDef container fill:#e6f2ff,stroke:#0066cc,stroke-width:2px
    classDef volume fill:#f2ffe6,stroke:#669900,stroke-width:2px
    classDef user fill:#ffe6e6,stroke:#cc0000,stroke-width:2px

    class DockerContainer container
    class VolumeMounts volume
    class UserInteraction user
```

## 9. Event Flow Diagram

```mermaid
flowchart TD
    %% Define all nodes first
    ParticipantImported[Participant Imported Event]
    RoundCreated[Round Created Event]
    WinnersSelected[Winners Selected Event]
    SessionCompleted[Session Completed Event]

    ParticipantService[Participant Service]
    RaffleService[Raffle Service]
    DrawService[Draw Service]

    LoggingSubscriber[Logging Subscriber]
    NotificationSubscriber[Notification Subscriber]
    AuditSubscriber[Audit Subscriber]

    %% Group related nodes
    subgraph DomainEvents["Domain Events"]
        ParticipantImported
        RoundCreated
        WinnersSelected
        SessionCompleted
    end

    subgraph Publishers["Publishers"]
        ParticipantService
        RaffleService
        DrawService
    end

    subgraph Subscribers["Subscribers"]
        LoggingSubscriber
        NotificationSubscriber
        AuditSubscriber
    end

    %% Define relationships with proper Mermaid syntax
    ParticipantService -- "publishes" --> ParticipantImported
    RaffleService -- "publishes" --> RoundCreated
    DrawService -- "publishes" --> WinnersSelected
    RaffleService -- "publishes" --> SessionCompleted

    ParticipantImported -- "handles" --> LoggingSubscriber
    ParticipantImported -- "handles" --> AuditSubscriber

    RoundCreated -- "handles" --> LoggingSubscriber

    WinnersSelected -- "handles" --> LoggingSubscriber
    WinnersSelected -- "handles" --> NotificationSubscriber
    WinnersSelected -- "handles" --> AuditSubscriber

    SessionCompleted -- "handles" --> LoggingSubscriber
    SessionCompleted -- "handles" --> AuditSubscriber
```

## 10. Data Flow Diagram

```mermaid
flowchart TD
    %% Define all nodes first
    User[User]
    DataSource[CSV Data Source]

    ImportParticipants[Import Participants Process]
    ValidateData[Validate Data Process]
    ConfigureRaffle[Configure Raffle Process]
    ExecuteDraw[Execute Draw Process]
    RecordResults[Record Results Process]

    ParticipantsStore[Participants Store]
    RoundsStore[Rounds Store]
    ResultsStore[Results Store]

    %% Group related nodes
    subgraph ExternalEntities["External Entities"]
        User
        DataSource
    end

    subgraph Processes["Processes"]
        ImportParticipants
        ValidateData
        ConfigureRaffle
        ExecuteDraw
        RecordResults
    end

    subgraph DataStores["Data Stores"]
        ParticipantsStore
        RoundsStore
        ResultsStore
    end

    %% Define relationships with proper Mermaid syntax
    DataSource -- "CSV file" --> ImportParticipants
    ImportParticipants -- "raw participant data" --> ValidateData
    ValidateData -- "valid participants" --> ParticipantsStore

    User -- "raffle configuration" --> ConfigureRaffle
    ConfigureRaffle -- "configured rounds" --> RoundsStore

    User -- "start draw command" --> ExecuteDraw
    ParticipantsStore -- "eligible participants" --> ExecuteDraw
    RoundsStore -- "round settings" --> ExecuteDraw
    ExecuteDraw -- "winners" --> RecordResults
    RecordResults -- "draw results" --> ResultsStore
    ResultsStore -- "display results" --> User
```

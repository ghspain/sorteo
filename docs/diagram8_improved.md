## 8. Deployment Diagram

This enhanced deployment diagram illustrates the complete deployment architecture for the raffle application, including containerization, volume management, networking, and runtime dependencies.

```mermaid
flowchart TD
    %% Development Environment
    subgraph DevelopmentEnv["Development Environment"]
        DevMachine["Developer Machine"]
        GitRepo["Git Repository"]
        CISystem["CI/CD Pipeline"]
    end

    %% Production Environment
    subgraph ProductionEnv["Production Environment"]
        subgraph DockerHost["Docker Host"]
            subgraph RaffleContainer["Raffle Application Container"]
                App["Raffle Application"]
                PythonRuntime["Python 3.10+ Runtime"]

                subgraph Dependencies["Application Dependencies"]
                    PythonLibs["Python Libraries"]
                    MockServices["Mock External Services"]
                end
            end

            subgraph NetworkConfig["Network Configuration"]
                DockerNetwork["Docker Network"]
                Ports["Exposed Ports: 8000"]
                HostConfig["Host Configuration"]
            end
        end

        subgraph PersistenceLayer["Persistence Layer"]
            subgraph VolumeMounts["Volume Mounts"]
                DataVolume["Data Volume: /app/data"]
                LogsVolume["Logs Volume: /app/logs"]
                ConfigVolume["Config Volume: /app/config"]
            end

            FileSystem["Host Filesystem"]
        end
    end

    %% User Environment
    subgraph UserEnv["User Environment"]
        UserCLI["Command Line Interface"]
        UserConfig["User Configuration Files"]
        LocalCSV["Local CSV Files"]
    end

    %% Build Process
    DevMachine -- "Push code" --> GitRepo
    GitRepo -- "Trigger build" --> CISystem
    CISystem -- "Build docker image" --> DockerHost

    %% Runtime Relationships
    UserCLI -- "Interacts via" --> Ports
    UserConfig -- "Mounted to" --> ConfigVolume
    LocalCSV -- "Imported to" --> DataVolume

    App -- "Runs on" --> PythonRuntime
    App -- "Uses" --> PythonLibs
    App -- "May use" --> MockServices

    App -- "Reads/Writes" --> DataVolume
    App -- "Writes logs to" --> LogsVolume
    App -- "Reads config from" --> ConfigVolume

    DataVolume -- "Persisted in" --> FileSystem
    LogsVolume -- "Persisted in" --> FileSystem
    ConfigVolume -- "Persisted in" --> FileSystem

    RaffleContainer -- "Connects via" --> DockerNetwork
    DockerNetwork -- "Configured via" --> HostConfig
    HostConfig -- "Exposes" --> Ports

    %% Styling
    classDef container fill:#e6f2ff,stroke:#0066cc,stroke-width:2px
    classDef volume fill:#f2ffe6,stroke:#669900,stroke-width:2px
    classDef user fill:#ffe6e6,stroke:#cc0000,stroke-width:2px
    classDef dev fill:#f2e6ff,stroke:#9900cc,stroke-width:2px

    class RaffleContainer,Dependencies container
    class VolumeMounts,DataVolume,LogsVolume,ConfigVolume volume
    class UserEnv,UserCLI,UserConfig,LocalCSV user
    class DevelopmentEnv,DevMachine,GitRepo,CISystem dev
```

This improved deployment diagram provides:

1. **Complete environment mapping**: Shows development, production, and user environments
2. **Build process**: Includes the CI/CD process from code to deployment
3. **Containerization details**: More explicit Docker configuration information
4. **Volume management**: Enhanced volume configuration with specific mount points
5. **Network configuration**: Shows how the application is exposed to users
6. **Dependency management**: Clearer representation of runtime dependencies
7. **User interaction**: Shows how users interact with the deployed application
8. **Data flow**: Visualizes how data moves between environments
9. **Enhanced styling**: Improved visual differentiation between components

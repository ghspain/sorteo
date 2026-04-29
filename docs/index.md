# GHSpain Sorteo Documentation

This site publishes the project documentation that lives in the repository under `docs/`.

## What You Will Find

- A practical overview of the Streamlit raffle application.
- The raffle workflow, including absent-winner redraw handling.
- Testing and verification commands.
- Architecture and sequence diagrams rendered directly from the repository documentation.

## Project Scope

The application supports event raffles driven by attendee CSV exports. It lets organizers:

- import participants,
- filter by check-in status,
- configure rounds and prizes,
- prevent repeated winners,
- redraw a replacement when a winner is absent,
- export the final results.

## Documentation Conventions

- The docs site is generated with MkDocs Material.
- Mermaid diagrams are rendered directly in GitHub Pages.
- Source diagrams remain in the repository so contributors can update them without rebuilding a frontend app.

## Main Links

- Repository: [ghspain/sorteo](https://github.com/ghspain/sorteo)
- Application README: [README.md](https://github.com/ghspain/sorteo/blob/main/README.md)

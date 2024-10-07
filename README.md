# FIVB Beach Volleyball Tournament API

This project provides an API for managing Beach Volleyball tournaments of Polish Federation of Volleyball, player rankings, and user authentication. The API allows organizers to create, update, and delete tournaments, manage player teams, and assign rankings based on tournament results.

Additionally, the project includes visual representations of API interactions using Django Templates, allowing users to interact with the system through a user-friendly web interface.

## API Endpoints

Here is an overview of the main API endpoints:

### Tournaments
- `GET /api/tournaments/`: Retrieve a list of all tournaments.
- `GET /api/tournaments/{id}/`: Retrieve details of a specific tournament.
- `POST /api/tournaments/`: Create a new tournament (requires organizer role).
- `PATCH /api/tournaments/{id}/`: Update an existing tournament.
- `DELETE /api/tournaments/{id}/`: Delete a tournament.

### Rankings
- `GET /api/ranking/`: Retrieve a list of all player rankings.
- `POST /api/ranking/`: Create or update rankings for players in a tournament.
- `GET /api/ranking/last-ranking/`: Retrieve the most recent rankings.

### Users
- `GET /api/users/`: Retrieve a list of all users.
- `POST /api/users/`: Register a new user.
- `PATCH /api/users/{id}/`: Update user information.
- `DELETE /api/users/{id}/`: Delete a user.

## Authentication

The API uses session-based authentication with cookies. To authenticate, send a request with valid session cookies (i.e., `sessionid`) for protected endpoints.

Example security scheme:
- `cookieAuth`: Uses a session cookie for authentication.

## Tournaments

The tournament endpoints allow authorized users (organizers) to create and manage tournaments. Each tournament includes information like name, city, type, sex (men or women), ranking, start and end dates, and participating teams.

### Example:
```json
{
  "id": 1,
  "name": "Beach Volleyball World Tour",
  "city": "Gdańsk",
  "date_of_beginning": "2024-07-12",
  "date_of_finishing": "2024-07-15",
  "money_prize": 50000,
  "ranking_display": "World Tour",
  "sex_display": "Men",
  "teams": [
    {"id": 1, "name": "Team A"},
    {"id": 2, "name": "Team B"}
  ]
}
```

## Rankings

The API supports storing and retrieving player rankings based on tournament results. Points are awarded based on the player's performance and the tournament type.

### Example ranking object:
```json
{
  "id": 1,
  "player": "John Doe",
  "points": 1200,
  "ranking_type": "World Tour",
  "date_of_update": "2024-07-16"
}
```

## Users

The user management system allows for registration, listing, and updating users. Each user is assigned a `user_type` which determines their role (`Zawodnik` or `Organizator`).

### Example user object:
```json
{
  "email": "johndoe@example.com",
  "imie": "John",
  "nazwisko": "Doe",
  "user_type": "PL",
  "gender": "Male",
  "pesel": null
}
```

## Visual Representation with Django Templates
The project also includes pages built using Django Templates to visually represent the interaction with the API. This feature allows users to:

View lists of tournaments and rankings directly in the browser.
Register for tournaments.
View personal rankings and tournament history.
Use forms to create and edit tournaments (for organizers).
These templates provide an intuitive user interface on top of the API, giving users an easy way to interact with the system without manually sending API requests.

Example Pages:
Tournament List: Displays all available tournaments.
Ranking Page: Shows the current rankings of players.
Tournament Details: Detailed view of each tournament, including teams and rankings.

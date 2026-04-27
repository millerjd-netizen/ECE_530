# Elevator API

quick rest api for an elevator system. EC530 lecture 5/6 assignment.

## what it does
- track floor, direction, door state
- accept floor requests
- list elevators in a building

still figuring out the queue logic

## run
## endpoints (so far)
- GET /elevators - list em
- GET /elevators/{id} - get one
- POST /elevators/{id}/request - send to a floor
- GET /elevators/{id}/status - current floor + state

TODO: error handling for invalid floors

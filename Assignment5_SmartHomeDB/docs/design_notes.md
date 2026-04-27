# Smart Home Database Design Notes

## Goal

The goal of this schema is to model a smart home system with users, houses, floors, rooms, devices, and sensor readings.

## Main Entities

- Users: people who can own or access houses
- Houses: physical smart home locations
- Ownership: junction table connecting users and houses
- Floors: levels inside a house
- Rooms: spaces inside a floor
- Devices: smart sensors or actuators assigned to rooms
- Sensor Readings: time-stamped measurements from devices

## Relationships

### Users to Houses

Users and houses have a many-to-many relationship.

A user can own multiple houses, and a house can have multiple users.

This is represented with the `ownership` junction table.

### Houses to Floors

A house can have many floors.

Each floor belongs to one house.

### Floors to Rooms

A floor can have many rooms.

Each room belongs to one floor.

### Rooms to Devices

A room can contain many devices.

Each device belongs to one room.

### Devices to Readings

A device can produce many sensor readings.

Each sensor reading belongs to one device.

## Soft Delete

Most main tables include an `is_deleted` column.

Instead of permanently deleting important objects, the system can mark them as deleted.

This supports safer data management and preserves history.

## Design Rationale

This schema uses a relational model because the smart home entities have clear relationships.

The schema supports:

- structured queries
- data integrity
- foreign key constraints
- future API development
- sensor history tracking

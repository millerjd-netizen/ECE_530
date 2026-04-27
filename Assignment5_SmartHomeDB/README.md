# Assignment 5: Smart Home Database Schema

## Overview

This assignment defines a relational database schema for a smart home system.

The system models users, houses, ownership, floors, rooms, devices, and sensor readings.

## Files

- `sql/schema.sql` — SQL schema definition
- `docs/design_notes.md` — explanation of entities and relationships

## Main Tables

- `users`
- `houses`
- `ownership`
- `floors`
- `rooms`
- `devices`
- `sensor_readings`

## Relationship Summary

- A user can own multiple houses.
- A house can have multiple users.
- A house contains floors.
- Floors contain rooms.
- Rooms contain devices.
- Devices generate sensor readings.

## Soft Delete

The schema uses `is_deleted` fields on major entities to support soft deletion instead of permanent deletion.

## How to Use

This schema can be loaded into SQLite:

```bash
sqlite3 smart_home.db < sql/schema.sql

Then run:

```bash
git log --oneline -5
cat > README.md <<'EOF'
# Assignment 5: Smart Home Database Schema

## Overview
This assignment defines a relational database schema for a smart home system.

## Files
- sql/schema.sql
- docs/design_notes.md

## Tables
- users
- houses
- ownership
- floors
- rooms
- devices
- sensor_readings

## Relationships
- Users ↔ Houses (many-to-many)
- Houses → Floors
- Floors → Rooms
- Rooms → Devices
- Devices → Sensor Readings

## Usage
sqlite3 smart_home.db < sql/schema.sql

# Assignment 6: Pub-Sub Messaging System

## Overview
This project implements a simple publisher-subscriber messaging system in Python.

## Features
- Event-based messaging model
- Topic-based subscriptions
- Broker routing system
- Decoupled publishers and subscribers
- Example math services
- Unit tests

## Structure
Assignment6_PubSubMessagingSystem/
├── src/
├── tests/
├── docs/
├── README.md

## Topics
- math.addition
- math.multiplication
- math.division

## Run Demo
python -m src.demo

## Run Tests
pytest

## Design
This system uses an in-memory broker to route events to subscribers based on topic.

Publishers do not know about subscribers.

Subscribers register interest in topics.

## Goal
Demonstrate a minimal but correct pub-sub architecture.

# Pub-Sub Messaging System Design Notes

## Goal

This project demonstrates a publisher-subscriber messaging pattern using a local Python broker.

The goal is to reduce direct coupling between senders and receivers.

## Main Components

### Event

The `Event` model represents a structured message.

Each event includes:

- topic
- event type
- payload
- event id
- timestamp

### Broker

The broker stores topic subscriptions and routes published events to matching subscribers.

Publishers do not know which subscribers will receive an event.

Subscribers only register interest in topics.

### Subscribers

Subscriber handlers are regular functions.

For this MVP, the subscribers perform math operations:

- addition
- multiplication
- division

## Topics

The system uses these topics:

- math.addition
- math.multiplication
- math.division

## Coupling Reduction

In direct communication, a sender must know the receiver.

In this pub-sub design, a sender only publishes an event to a topic.

The broker handles routing.

## Example Flow

1. A publisher creates an `AdditionRequested` event.
2. The event is published to `math.addition`.
3. The broker finds all subscribers for `math.addition`.
4. The addition handler processes the event.
5. The handler returns a result.

## Limitations

This MVP uses an in-memory broker.

It does not persist messages.

It does not handle networked nodes.

It does not use Redis.

Those features could be added later without changing the main event model.

import redis
import json
import threading
import os
import time

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_CHANNEL = 'bookstore_events'

def publish_event(event_name, data):
    """Publish an event to the Redis channel."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=5)
        message = json.dumps({'event': event_name, 'data': data})
        r.publish(REDIS_CHANNEL, message)
        print(f"[Event Broker] Published {event_name} with data: {data}")
    except Exception as e:
        print(f"[Event Broker] Error publishing event {event_name}: {e}")

def start_consumer(event_handlers):
    """Start a background daemon thread that listens for Redis events."""
    def run():
        time.sleep(3)
        while True:
            try:
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=None)
                pubsub = r.pubsub()
                pubsub.subscribe(REDIS_CHANNEL)
                print(f"[Event Broker] Subscribed to {REDIS_CHANNEL}. Listening...")
                
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            payload = json.loads(message['data'])
                            event_name = payload.get('event')
                            data = payload.get('data')
                            if event_name in event_handlers:
                                print(f"[Event Broker] Handling event: {event_name}")
                                from django.db import close_old_connections
                                close_old_connections()
                                event_handlers[event_name](data)
                                close_old_connections()
                        except Exception as e:
                            print(f"[Event Broker] Error processing message payload: {e}")
            except Exception as e:
                print(f"[Event Broker] Consumer error: {e}. Reconnecting in 5 seconds...")
                time.sleep(5)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

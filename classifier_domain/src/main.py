import kafka_interface as kafka
import os, json
import classifier
import mongodb_interface as mongo

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TOPIC_INPUT = os.environ.get('TOPIC_INPUT')
TOPIC_OUTPUT = os.environ.get('TOPIC_OUTPUT')
MESSAGES_PER_SECOND = float(os.environ.get('MESSAGES_PER_SECOND'))
SLEEP_TIME = 1 / MESSAGES_PER_SECOND
TRAINING_SET = os.environ.get('TRAINING_SET')
TRAINING_PARQUET = os.environ.get('TRAINING_PARQUET')
MODEL = os.environ.get('MODEL')



def main():
    print('Loading the model...')
    model = classifier.load_classifier(model = MODEL, parquet = TRAINING_PARQUET, training_set = TRAINING_SET)
    print('Running Consumer...')
    try:
        partitioner = kafka.get_RoundRobin_partitioner_for_topic(TOPIC_OUTPUT,KAFKA_BROKER_URL)
    except Exception as ex:
        print('Error with topic partitions')
        print(ex)
    try:
        consumer = kafka.connectConsumer(topic = TOPIC_INPUT, server = KAFKA_BROKER_URL)
        print("Consumer connected")
    except Exception as ex:
        print("Error connecting kafka broker as Consumer")
        print(ex)
    try:
        producer = kafka.connectProducer(server = KAFKA_BROKER_URL, partitioner = partitioner)
        print("Producer connected")
    except Exception as ex:
        print("Error connecting kafka broker as Producer")
        print(ex)
    i=0
    working = True
    while working:
        message_dict = kafka.consume(consumer = consumer)
        if (message_dict != {}):
            for topic, messages in message_dict.items():
                for message in messages:
                    if classifier.predict(model = model, input = message.value['url_page']) == 1:
                        collection = 'Classifier'
                        mongo.put(collection, json.dumps(message.value))
                        print('Data saved on db: collection: ' + str(collection) + ' url: ' + message.value['url_page'])

                        kafka.send_message(producer = producer, key =i, topic = TOPIC_OUTPUT, message = message.value)
                    i=i+1
if __name__ == '__main__':
    main()


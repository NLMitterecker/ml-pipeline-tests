# original file: https://github.com/GoogleCloudPlatform/ml-design-patterns/blob/master/04_hacking_training_loop/checkpoints.ipynb
import tensorflow as tf
from tensorflow.python.framework import dtypes
from tensorflow_io.bigquery import BigQueryClient
from tensorflow_io.bigquery import BigQueryReadSession

def features_and_labels(features):
  label = features.pop('tolls_amount') # this is what we will train for
  return features, tf.cast(label > 0, dtypes.int64, name='threshold')

def read_dataset(client, row_restriction, batch_size=2048, infinite=True):
    GCP_PROJECT_ID='ai-analytics-solutions'  # CHANGE
    COL_NAMES = ['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude', 'tolls_amount']
    COL_TYPES = [dtypes.float64] * len(COL_NAMES)
    DATASET_GCP_PROJECT_ID, DATASET_ID, TABLE_ID,  = 'bigquery-public-data.new_york.tlc_green_trips_2015'.split('.')
    bqsession = client.read_session(
        "projects/" + GCP_PROJECT_ID,
        DATASET_GCP_PROJECT_ID, TABLE_ID, DATASET_ID,
        COL_NAMES, COL_TYPES,
        requested_streams=2,
        row_restriction=row_restriction + ' AND pickup_longitude > -80 AND dropoff_longitude < -70')
    dataset = bqsession.parallel_read_rows()
    dataset = dataset.prefetch(1).map(features_and_labels).shuffle(batch_size*10).batch(batch_size)
    if infinite:
        dataset = dataset.repeat()
    return dataset

client = BigQueryClient()


temp_df = read_dataset(client, "pickup_datetime BETWEEN '2015-01-01' AND '2015-03-31'", 2)
for row in temp_df:
    print(row)
    break
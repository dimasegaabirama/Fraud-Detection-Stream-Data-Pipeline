from pyflink.common import Types
from pyflink.datastream import OutputTag

FRAUD_RESULTS = OutputTag("fraud_results", Types.PICKLED_BYTE_ARRAY())

from pyflink.common import Types
from pyflink.datastream import OutputTag

DEAD_LETTER_TAG = OutputTag("dead_letter", Types.PICKLED_BYTE_ARRAY())
DUPLICATE_TAG = OutputTag("duplicates", Types.PICKLED_BYTE_ARRAY())

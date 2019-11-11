import utils
import time

while True:
    result = utils.selectDb("e0f694b52142")
    lastDttm = ""
    # for one in result:
    #     print ( one )
    if( len(result) > 0 ):
        lastDttm = result[len( result) -1][1]
    print ( "---DataSize is:"+str( len( result ) ) )
    print ( "---LastDttm is:"+ lastDttm )
    result = utils.deleteDb("e0f694b52142", lastDttm)
    time.sleep(5)


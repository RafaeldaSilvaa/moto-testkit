from aws_testkit.src import MotoTestKit, S3ObjectModel

kit = MotoTestKit(auto_start=False, auto_stop_on_exit=True)  # default
# a primeira chamada a get_client inicia o moto automaticamente
s3 = kit.get_client("s3")
s3.create_bucket(Bucket="script-bucket")

# usa helpers typed (sync)
s3h = kit.s3_helper()
s3h.create_bucket(bucket="test")
obj = S3ObjectModel(bucket="script-bucket", key="x.txt", body=b"hello")
s3h.put_object(obj)

# não precisa call kit.stop(); atexit tentará finalizar ao terminar o processo
print("Wrote object to script-bucket")

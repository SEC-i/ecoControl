from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sensors, time

engine = create_engine('postgresql://bp2013h1:hirsch@172.16.22.247:5432/protodb')
 
Base = declarative_base()

class Measure(Base):
     __tablename__ = 'fabian_temperatures'

     id = Column(Integer, primary_key=True)
     time = Column(DateTime)
     cpu_temp = Column(Integer)
     gpu_temp = Column(Integer)
     
     def __init__(self, time, cpu, gpu):
        self.time = time
        self.cpu_temp = cpu
        self.gpu_temp = gpu
     
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def getTemp():
  sensors.init()
  try:
        chips = sensors.iter_detected_chips()
        cpu = chips.next()
        gpu = chips.next()
        cpu_iter = iter(cpu)
        gpu_iter = iter(gpu)
        cpu_temp = cpu_iter.next().get_value()
        gpu_temp = gpu_iter.next().get_value()
  finally:
        sensors.cleanup()
  return cpu_temp, gpu_temp

while True:
  cpu,gpu = getTemp()
  session.add( Measure(time.asctime(), cpu, gpu) )
  session.commit()
  time.sleep(5)

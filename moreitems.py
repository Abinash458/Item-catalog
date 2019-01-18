from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from sqlalchemy_utils import database_exists, drop_database, create_database

from database_setup import Base, User, Brand, BrandModel

engine = create_engine('sqlite:///carsmodel.db')

# clear database
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
"""A DBSession() instance establishes all conversations with the database
and represents a "staging zone" for all the objects loaded into the
database session object. Any change made against the objects in the
session won't be persisted into the database until you call
session.commit(). If you're not happy about the changes, you can
revert all of them back to the last commit by calling session.rollback()"""
session = DBSession()

# Create dummy user
user1 = User(
    name="Mahmohan Shing",
    email="abinashmohapatra1998@gmail.com",
    picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

# Audi Models
brand1 = Brand(name='Audi', user_id=1)
session.add(brand1)
session.commit()

brand_model1 = BrandModel(
    name="Audi Q2",
    user_id=1,
    description="The Audi Q2 is a mini SUV developed and manufactured by Audi. It was first unveiled to the public on 1 March 2016, at the 2016 Geneva Motor Show. The vehicle, which is being manufactured at the Audi headquarters in Ingolstadt, Germany, is based on Volkswagen's MQB platform.",
    brand=brand1)
session.add(brand_model1)
session.commit()

brand_model2 = BrandModel(
    name="Audi R8",
    user_id=1,
    description="The Audi R8 is a mid-engine, 2-seater sports car, which uses Audi's trademark quattro permanent all-wheel drive system. It was introduced by the German car manufacturer Audi AG in 2006.",
    brand=brand1)
session.add(brand_model2)
session.commit()

brand_model3 = BrandModel(
    name="Audi S1",
    user_id=1,
    description="The Audi S1 is Audi's smallest S model car and a performance version of the Audi A1. The first variant (Typ 8X, produced from 2010 to 2018) has 228 hp (231 PS / 170 kW) derived from the Volkswagen group's EA888 2.0 litre turbo four cylinder, and permanent quattro four wheel drive.",
    brand=brand1)
session.add(brand_model3)
session.commit()

# BMW Models
brand2 = Brand(name='BMW', user_id=1)
session.add(brand2)
session.commit()

brand_model1 = BrandModel(
    name="BMW 2-Series",
    user_id=1,
    description="The BMW 2 Series is a subcompact executive car (C-segment) produced by BMW. The 2 Series has several different body styles.",
    brand=brand2)
session.add(brand_model1)
session.commit()

brand_model2 = BrandModel(
    name="BMW i8",
    user_id=1,
    description="The BMW i8 is a plug-in hybrid sports car developed by BMW. The 2015 model year BMW i8 has a 7.1 kWh lithium-ion battery pack that delivers an all-electric range of 37 km (23 mi) under the New European Driving Cycle.",
    brand=brand2)
session.add(brand_model2)
session.commit()

brand_model3 = BrandModel(
    name="BMW i3",
    user_id=1,
    description="The BMW i3 is a B-class, high-roof hatchback manufactured and marketed by BMW with an electric powertrain using rear wheel drive via a single-speed transmission and featuring an underfloor Li-ion battery pack.",
    brand=brand2)
session.add(brand_model3)
session.commit()

# FORD Models
brand3 = Brand(name='FORD', user_id=1)
session.add(brand3)
session.commit()

brand_model1 = BrandModel(
    name="Ford Mustang",
    user_id=1,
    description="The Ford Mustang is an American car manufactured by Ford. It was originally based on the platform of the second generation North American Ford Falcon, a compact car.",
    brand=brand3)
session.add(brand_model1)
session.commit()

brand_model2 = BrandModel(
    name="Ford EcoSport",
    user_id=1,
    description="The Ford EcoSport (pronounced ek-ho sport) is a subcompact crossover SUV, originally built in Brazil by Ford Brazil since 2003, at the Camacari plant.",
    brand=brand3)
session.add(brand_model2)
session.commit()

brand_model3 = BrandModel(
    name="Ford Thunderbird",
    user_id=1,
    description="Ford Thunderbird (colloquially called the T-Bird) is a nameplate that was used by Ford from 1955 to 1997 and 2002 to 2005 over eleven model generations.",
    brand=brand3)
session.add(brand_model3)
session.commit()

# Volvo Models
brand4 = Brand(name='VOLVO', user_id=1)
session.add(brand4)
session.commit()

brand_model1 = BrandModel(
    name="Volvo XC60",
    user_id=1,
    description="The Volvo XC60 is a compact luxury crossover SUV manufactured and marketed by Swedish automaker Volvo Cars since 2008. It is now in its second generation.",
    brand=brand4)
session.add(brand_model1)
session.commit()

brand_model2 = BrandModel(
    name="Volvo C30",
    user_id=1,
    description="The Volvo C30 is a three-door, front-engine, front-wheel-drive premium compact hatchback, manufactured and marketed by Volvo Cars for model years 2006-2013 in a single generation.",
    brand=brand4)
session.add(brand_model2)
session.commit()

brand_model3 = BrandModel(
    name="Volvo V50",
    user_id=1,
    description="Volvo Cars introduced the Volvo V50 at the 2003 Bologna Motor Show as the station wagon version of the Volvo S40 small family car manufacturing both models at their facility in Ghent, Belgium.",
    brand=brand4)
session.add(brand_model3)
session.commit()

# Aston Martin
brand5 = Brand(name='Auston Martin', user_id=1)
session.add(brand5)
session.commit()


brands = session.query(Brand).all()
for brand in brands:
    print "Brand: " + brand.name

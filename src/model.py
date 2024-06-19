from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import create_engine, Column
from sqlalchemy.orm     import sessionmaker
from sqlalchemy                 import (Integer, String, Date, DateTime, Float, Boolean, Text)
import random
import re
def create_table(engine):
    Base.metadata.create_all(engine)

Base = declarative_base()
db_name = 'subito_crypto.db'
engine = create_engine(f'sqlite:///{db_name}')
create_table(engine)
session = sessionmaker(bind=engine)()

livelli = [0, 100, 235, 505, 810, 1250, 1725, 2335, 2980, 3760, 4575, 5525, 6510, 7630, 8785, 10075, 11400, 12860, 14355, 15985, 17650, 19450, 21285, 23255, 25260, 27400, 29575,
31885, 34230, 36710, 39225, 41875, 44560, 47380, 50235, 53225, 56250, 59410, 62605, 65935,70000,75000,80000,85000,90000,95000,100000,105000]

class Database:
    def __init__(self):
        engine = create_engine(f'sqlite:///{db_name}')
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

class Utente(Base):
    __tablename__ = "utente"
    id = Column(Integer, primary_key=True)
    id_telegram = Column('id_Telegram', Integer, unique=True)
    nome  = Column('nome', String(32))
    cognome = Column('cognome', String(32))
    username = Column('username', String(32), unique=True)
    exp = Column('exp', Integer)
    trustscore = Column('trustscore', Integer)
    livello = Column('livello', Integer)
    admin = Column('admin',Integer)
    
    
    def CreateUser(self,id_telegram,username,name,last_name):
        session = Database().Session()
        user = session.query(Utente).filter_by(id_telegram = id_telegram).first()
        if user is None:
            try:
                utente = Utente()
                utente.username     = username
                utente.nome         = name
                utente.id_telegram  = id_telegram
                utente.cognome      = last_name
                utente.exp          = 0
                utente.livello      = 1
                utente.trustscore  = 0
                utente.admin        = 0
                session.add(utente)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
        elif user.username!=username:
            self.update_user(id_telegram,{'username':username,'nome':name,'cognome':last_name})
        return user

    def getUtente(self, target):
        utente = None
        target = str(target)

        if target.startswith('@'):
            utente = session.query(Utente).filter_by(username=target).first()
        else:
            chatid = int(target) if target.isdigit() else None
            if chatid is not None:
                utente = session.query(Utente).filter_by(id_telegram=chatid).first()

        return utente

    def getUtenteByMessage(self,message):
        if message.chat.type == "group" or message.chat.type == "supergroup":
            chatid =        message.from_user.id
        elif message.chat.type == 'private':
            chatid = message.chat.id    
        return self.getUtente(chatid)

    def checkUtente(self, message):
        if message.chat.type == "group" or message.chat.type == "supergroup":
            chatid =        message.from_user.id
            username =      '@'+message.from_user.username
            name =          message.from_user.first_name
            last_name =     message.from_user.last_name
        elif message.chat.type == 'private':
            chatid = message.chat.id
            username = '@'+str(message.chat.username)
            name = message.chat.first_name
            last_name = message.chat.last_name
        user = self.CreateUser(id_telegram=chatid,username=username,name=name,last_name=last_name)
        self.addRandomExp(user,message)

    def isAdmin(self,utente):
        session = Database().Session()
        if utente:
            exist = session.query(Utente).filter_by(id_telegram = utente.id_telegram,admin=1).first()
            return False if exist is None else True
        else:
            return False


    def infoUser(self, utente):
        nome_utente = utente.nome if utente.username is None else utente.username
        exp_to_lv = livelli[utente.livello]
        answer = ""
        answer += f"*👤 {nome_utente}*\n"
        answer += f"*🤝 Trust Score*: {utente.trustscore}\n"
        answer += f"*💪🏻 Exp*: {utente.exp}/{exp_to_lv}\n"
        answer += f"*🎖 Lv. *{utente.livello}\n"

        return answer

    def addRandomExp(self,user,message):
        exp = random.randint(1,5)
        self.addExp(user,exp)
        
    def addExp(self,utente,exp):
        exp_to_lv = livelli[utente.livello]
        newexp = utente.exp+exp
        if newexp>=exp_to_lv:
            newlv = utente.livello + 1
        else:
            newlv = utente.livello
        self.update_user(utente.id_telegram,{'exp':newexp,'livello':newlv})

    def update_table_entry(self, table_class, filter_column, filter_value, update_dict):
        session = Database().Session()
        table_entry = session.query(table_class).filter_by(**{filter_column: filter_value}).first()
        for key, value in update_dict.items():
            setattr(table_entry, key, value)
        session.commit()
        session.close()

    def update_user(self, chatid, kwargs):
        self.update_table_entry(Utente, "id_telegram", chatid, kwargs)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    id_telegram = Column('id_Telegram', Integer, unique=True)
    positivo = Column('positivo',Integer)
    commento = Column('commento',Text)

    def createFeedback(self, id_telegram, positivo, commento):
        session = Database().Session()
        feedback = Feedback(id_telegram=id_telegram, positivo=positivo, commento=commento)
        session.add(feedback)
        session.commit()
        session.close()
        return feedback

    def getFeedbacks(self, id_telegram):
        session = Database().Session()
        feedback = session.query(Feedback).filter_by(id_telegram=id_telegram).all()
        session.close()
        return feedback


class Gruppo(Base):
    __tablename__ = "gruppo"
    id = Column(Integer, primary_key=True)
    nome = Column('nome', String(128))
    chat_id = Column('chat_id', Integer, unique=True)

    def addGruppo(self, nome, chat_id):
        session = Database().Session()
        gruppo = Gruppo(nome=nome, chat_id=chat_id)
        session.add(gruppo)
        session.commit()
        session.close()

    def getGruppoByChatId(self, chat_id):
        session = Database().Session()
        gruppo = session.query(Gruppo).filter_by(chat_id=chat_id).first()
        session.close()
        return gruppo

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    hashtag = Column('hashtag', String(64))
    messaggio = Column('messaggio', Text)
    id_utente = Column('id_utente', Integer)

    def addTag(self, hashtag, messaggio, id_utente):
        session = Database().Session()
        tag = Tag(hashtag=hashtag, messaggio=messaggio, id_utente=id_utente)
        session.add(tag)
        session.commit()
        session.close()

    def getTagsByMessage(self, messaggio):
        session = Database().Session()
        tags = session.query(Tag).filter_by(messaggio=messaggio).all()
        session.close()
        return tags

    def getTagsByHashtag(self, hashtag):
        session = Database().Session()
        tags = session.query(Tag).filter_by(hashtag=hashtag).all()
        session.close()
        return tags

    def getTagsByMessage(self, messaggio):
        
        # Extract hashtags using regular expression
        hashtag_regex = r"#(\w+)"
        hashtags = re.findall(hashtag_regex, messaggio)

        # Create a list of Tag objects
        tags = []
        for hashtag in hashtags:
            tags.append(hashtag)

        return tags
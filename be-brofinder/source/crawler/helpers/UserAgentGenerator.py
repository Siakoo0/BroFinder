from random import choice

from source.crawler.helpers.Singleton import Singleton

class UserAgentGenerator(metaclass=Singleton):
    __user_agents = {}
    
    @classmethod
    def getUserAgents(cls):
        return cls.__user_agents

    @classmethod
    def generate(cls):
        if not len(cls.__user_agents):
            with open("./source/crawler/helpers/db-1.txt", "r") as f:
                cls.__user_agents = {user_agent : 0 for user_agent in f.read().split("\n")}

        user_agent = choice(list(cls.__user_agents.keys()))
        cls.__user_agents[user_agent] += 1

        return user_agent
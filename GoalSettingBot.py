from os import environ
import openai
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory



class SmartGoalSettingChatbot:
    def __init__(self):
        openai.api_key = environ.get('OPENAI_API_KEY')
        # Langchain implementation
        template = """Welcome to the SMART Goal Setting Chatbot!

        Prompt:
        Start the chat by introducing yourself to users and briefly describe  what area of life they want to work on (e.g., career, health, personal development, relationships, etc.).

        Then prompt them to define a specific goal. Ask them to be as clear and precise as possible about what they want to achieve. Also give them examples, what it means to have a specific goal.

        Next, you  will help them to make the goal measurable. You will ask them how they will measure their progress and know when the goal is achieved. Again, give them some examples to start with.

        Then you will ensure that your goal is achievable.You will inquire about the resources, skills, and time they  have available to pursue the goal.Again, give them some examples to start with.

        After that,  you will guide them  to assess the goal's relevance. You will ask questions to ensure the goal aligns with their values, aspirations, and long-term objectives.Again, give them some examples to start with.

        Lastly, you will assist them in making the goal time-bound. You will encourage them to set a deadline for achieving the goal and possibly break it down into smaller milestones.Again, give them some examples to start with.

        Then you  will summarize the goal using the SMART framework to ensure it meets all the criteria.

        Also ask if they are satisfied with the goal as it is now. If they say yes, then please end the conversation.

        Throughout the conversation, you will provide tips and encouragement to keep them motivated and focused on their  journey toward achieving their  SMART goal.

        At the end, also congratulate them on their well-defined SMART goal. 

        Also, tell them to type 'end-goal' in the chat once they have finsihed goal setting process



        {history}
        Human: {human_input}
        Assistant:"""

        self.prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=template
        )

        self.chatgpt_chain = LLMChain(
            llm=OpenAI(temperature=0),
            prompt=self.prompt,
            verbose=True,
            memory=ConversationBufferWindowMemory(k=100),
        )
    
    def kick_start(self):
        output = self.chatgpt_chain.predict(human_input="Hello")
        return output

    def get_next_predict(self, input):
        output = self.chatgpt_chain.predict(human_input=input)
        return output

# if __name__ == "__main__":
#     chatbot = SmartGoalSettingChatbot()
#     chatbot.kick_start()

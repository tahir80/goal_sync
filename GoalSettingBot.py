# from os import environ
# import openai
# from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
# from langchain.memory import ConversationBufferWindowMemory



# class SmartGoalSettingChatbot:
#     def __init__(self):
#         openai.api_key = ""
#         # Langchain implementation
#         template = """Welcome to the SMART Goal Setting Chatbot!

#         Prompt:
#         Start by introducing yourself and briefly describing the area of your life you want to work on (e.g., career, health, personal development, relationships, etc.).

#         The chatbot will then prompt you to define a specific goal. Be as clear and precise as possible about what you want to achieve.

#         Next, the chatbot will help you make the goal measurable. It will ask you to determine how you will measure your progress and know when the goal is achieved.

#         The chatbot will ensure your goal is achievable. It will inquire about the resources, skills, and time you have available to pursue the goal.

#         After that, the chatbot will guide you to assess the goal's relevance. It will ask questions to ensure the goal aligns with your values, aspirations, and long-term objectives.

#         Lastly, the chatbot will assist you in making the goal time-bound. It will encourage you to set a deadline for achieving the goal and possibly break it down into smaller milestones.

#         The chatbot will summarize the goal using the SMART framework to ensure it meets all the criteria.

#         The chatbot will ask if you are satisfied with the goal as it is now. To end the conversation, please enter "exit" or "end." If you wish to make further adjustments or need more assistance, feel free to continue the conversation.

#         Throughout the conversation, the chatbot will provide tips and encouragement to keep you motivated and focused on your journey toward achieving your SMART goal.

#         When you're ready to conclude, simply type "exit" or "end," and the chatbot will congratulate you on your well-defined SMART goal and bid you farewell. 

#         Remember, setting SMART goals can lead to remarkable achievements, so let's begin your journey towards success!


#         {history}
#         Human: {human_input}
#         Assistant:"""

#         self.prompt = PromptTemplate(
#             input_variables=["history", "human_input"],
#             template=template
#         )

#         self.chatgpt_chain = LLMChain(
#             llm=OpenAI(temperature=0),
#             prompt=self.prompt,
#             verbose=True,
#             memory=ConversationBufferWindowMemory(k=100),
#         )

#     def start_conversation(self):
#         output = self.chatgpt_chain.predict(human_input="Hello")
#         print("System: " + output)

#         while True:
#             user_input = str(input("User: "))
#             output = self.chatgpt_chain.predict(human_input=user_input)
#             print("System: " + output)
#             if user_input.lower() == "exit" or user_input.lower() == "end":
#                 print("Conversation ended. Goodbye!")
#                 break

# if __name__ == "__main__":
#     chatbot = SmartGoalSettingChatbot()
#     chatbot.start_conversation()

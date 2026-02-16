import json

from sqlalchemy.orm import Session

from backend.models.ai_conversation import AIConversation


class AIService:
    def __init__(self, db: Session):
        self.db = db

    def chat(self, user_id: str, message: str, conversation_id: int | None = None) -> dict:
        from puffin.ai import ClaudeProvider
        provider = ClaudeProvider()
        response = provider.generate(message)
        if conversation_id:
            conv = self.db.query(AIConversation).filter(
                AIConversation.id == conversation_id, AIConversation.user_id == user_id
            ).first()
            if conv:
                messages = json.loads(conv.messages)
                messages.append({"role": "user", "content": message})
                messages.append({"role": "assistant", "content": response})
                conv.messages = json.dumps(messages)
                self.db.commit()
        else:
            messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response},
            ]
            conv = AIConversation(user_id=user_id, messages=json.dumps(messages))
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)
        return {"conversation_id": conv.id, "response": response}

    def analyze_sentiment(self, text: str) -> dict:
        try:
            from puffin.nlp import RuleSentiment
            analyzer = RuleSentiment()
            result = analyzer.analyze(text)
            return {"sentiment": result}
        except ImportError:
            from puffin.ai import analyze_sentiment
            result = analyze_sentiment(text)
            return {"sentiment": result}

    def extract_topics(self, documents: list[str], n_topics: int = 5) -> dict:
        from puffin.nlp import LDAModel
        model = LDAModel(n_topics=n_topics)
        model.fit(documents)
        return {"topics": model.get_topics()}

    def get_conversations(self, user_id: str) -> list[AIConversation]:
        return self.db.query(AIConversation).filter(AIConversation.user_id == user_id).all()

"""Conversation memory with vector store integration.

This module provides conversation history management with vector embeddings
for semantic search through past conversations.
"""

import os
import json
import time
import hashlib
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

import numpy as np
from hanzo_mcp.types import MCPResourceDocument
from hanzo_mcp.tools.common.base import BaseTool


class MessageRole(Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a message in conversation."""
    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            # Generate unique ID
            content_hash = hashlib.md5(
                f"{self.role.value}{self.content}{self.timestamp}".encode()
            ).hexdigest()[:8]
            self.id = f"msg_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
        
        if self.embedding is not None:
            data["embedding"] = self.embedding.tolist()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        embedding = None
        if "embedding" in data:
            embedding = np.array(data["embedding"])
        
        return cls(
            id=data.get("id"),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
            embedding=embedding,
        )


@dataclass
class Conversation:
    """Represents a conversation session."""
    id: str
    messages: List[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    
    def add_message(self, message: Message):
        """Add message to conversation."""
        self.messages.append(message)
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "summary": self.summary,
            "topics": self.topics,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create from dictionary."""
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        
        return cls(
            id=data["id"],
            messages=messages,
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            metadata=data.get("metadata", {}),
            summary=data.get("summary"),
            topics=data.get("topics", []),
        )


class EmbeddingProvider:
    """Provides text embeddings for vector search."""
    
    def __init__(self, model: str = "local"):
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        if model == "local":
            # Use simple TF-IDF or word embeddings
            self._init_local_embedder()
        elif model == "openai":
            # Use OpenAI embeddings
            self._init_openai_embedder()
        elif model == "sentence-transformers":
            # Use sentence transformers
            self._init_sentence_transformers()
    
    def _init_local_embedder(self):
        """Initialize local embedder."""
        # Simple word vector approach
        self.vocab = {}
        self.embedding_dim = 384
    
    def _init_openai_embedder(self):
        """Initialize OpenAI embedder."""
        # Requires OpenAI API key
        pass
    
    def _init_sentence_transformers(self):
        """Initialize sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384
        except ImportError:
            self.logger.warning("sentence-transformers not installed, falling back to local")
            self._init_local_embedder()
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        
        if self.model == "local":
            # Simple hash-based embedding
            words = text.lower().split()
            embedding = np.zeros(self.embedding_dim)
            
            for word in words:
                # Hash word to get consistent index
                index = hash(word) % self.embedding_dim
                embedding[index] += 1
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
        
        elif self.model == "sentence-transformers":
            # Use sentence transformers
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                embedding = model.encode(text)
                return embedding
            except:
                # Fallback to local
                return await self.embed_text(text)
        
        else:
            # Placeholder for other models
            return np.random.randn(self.embedding_dim)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


class ConversationMemory(BaseTool):
    """Conversation memory with vector search."""
    
    name = "conversation_memory"
    description = """Manage conversation history with vector search.
    
    Actions:
    - add: Add message to current conversation
    - search: Search through conversation history
    - recall: Recall specific conversation
    - summarize: Summarize conversation
    - topics: Extract topics from conversation
    - export: Export conversations
    - import: Import conversations
    - stats: Get memory statistics
    
    This tool maintains conversation history with vector embeddings
    for semantic search across all past conversations.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Storage
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".hanzo" / "conversations"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Current conversation
        self.current_conversation_id = self._generate_conversation_id()
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation = Conversation(id=self.current_conversation_id)
        self.conversations[self.current_conversation_id] = self.current_conversation
        
        # Embeddings
        self.embedder = EmbeddingProvider(model="local")
        
        # Load existing conversations
        self._load_conversations()
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(os.urandom(16)).hexdigest()[:6]
        return f"conv_{timestamp}_{random_suffix}"
    
    def _load_conversations(self):
        """Load conversations from storage."""
        for conv_file in self.storage_path.glob("conv_*.json"):
            try:
                with open(conv_file, "r") as f:
                    data = json.load(f)
                    conv = Conversation.from_dict(data)
                    self.conversations[conv.id] = conv
            except Exception as e:
                self.logger.error(f"Failed to load {conv_file}: {e}")
    
    def _save_conversation(self, conversation: Conversation):
        """Save conversation to storage."""
        conv_file = self.storage_path / f"{conversation.id}.json"
        
        with open(conv_file, "w") as f:
            json.dump(conversation.to_dict(), f, indent=2)
    
    async def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add message to current conversation."""
        
        # Create message
        message = Message(
            role=MessageRole(role.lower()),
            content=content,
            metadata=metadata or {},
        )
        
        # Generate embedding
        message.embedding = await self.embedder.embed_text(content)
        
        # Add to conversation
        self.current_conversation.add_message(message)
        
        # Save periodically
        if len(self.current_conversation.messages) % 10 == 0:
            self._save_conversation(self.current_conversation)
        
        return message
    
    async def search_messages(
        self,
        query: str,
        limit: int = 10,
        conversation_id: Optional[str] = None,
        role_filter: Optional[str] = None,
    ) -> List[Tuple[Message, float, str]]:
        """Search messages using vector similarity."""
        
        # Generate query embedding
        query_embedding = await self.embedder.embed_text(query)
        
        # Search across conversations
        results = []
        
        conversations = (
            [self.conversations[conversation_id]]
            if conversation_id and conversation_id in self.conversations
            else self.conversations.values()
        )
        
        for conv in conversations:
            for msg in conv.messages:
                # Apply role filter
                if role_filter and msg.role.value != role_filter:
                    continue
                
                # Calculate similarity
                if msg.embedding is not None:
                    similarity = self.embedder.cosine_similarity(
                        query_embedding, msg.embedding
                    )
                    
                    results.append((msg, similarity, conv.id))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    async def summarize_conversation(
        self,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Generate conversation summary."""
        
        conv = (
            self.conversations.get(conversation_id, self.current_conversation)
            if conversation_id
            else self.current_conversation
        )
        
        if not conv.messages:
            return "No messages in conversation"
        
        # Simple extractive summary
        # In production, use LLM for abstractive summary
        important_messages = []
        
        for msg in conv.messages:
            if msg.role == MessageRole.USER:
                # Include user questions
                important_messages.append(f"User: {msg.content[:100]}...")
            elif msg.role == MessageRole.ASSISTANT:
                # Include key assistant responses
                if any(keyword in msg.content.lower() for keyword in
                      ["important", "summary", "conclusion", "result"]):
                    important_messages.append(f"Assistant: {msg.content[:100]}...")
        
        summary = "\n".join(important_messages[:5])
        
        # Store summary
        conv.summary = summary
        self._save_conversation(conv)
        
        return summary
    
    async def extract_topics(
        self,
        conversation_id: Optional[str] = None,
    ) -> List[str]:
        """Extract topics from conversation."""
        
        conv = (
            self.conversations.get(conversation_id, self.current_conversation)
            if conversation_id
            else self.current_conversation
        )
        
        # Simple keyword extraction
        # In production, use NLP for topic modeling
        text = " ".join(msg.content for msg in conv.messages)
        words = text.lower().split()
        
        # Count word frequencies
        word_freq = {}
        stopwords = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "but"}
        
        for word in words:
            if word not in stopwords and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top topics
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topic_words = [word for word, freq in topics[:10] if freq > 2]
        
        # Store topics
        conv.topics = topic_words
        self._save_conversation(conv)
        
        return topic_words
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        
        total_messages = sum(len(c.messages) for c in self.conversations.values())
        total_conversations = len(self.conversations)
        
        # Message distribution
        role_distribution = {}
        for conv in self.conversations.values():
            for msg in conv.messages:
                role = msg.role.value
                role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Storage size
        total_size = sum(
            f.stat().st_size
            for f in self.storage_path.glob("conv_*.json")
        )
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "current_conversation_id": self.current_conversation_id,
            "current_conversation_messages": len(self.current_conversation.messages),
            "role_distribution": role_distribution,
            "storage_size_bytes": total_size,
            "storage_size_mb": total_size / (1024 * 1024),
        }
    
    def export_conversations(
        self,
        format: str = "json",
        conversation_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Export conversations."""
        
        conversations = (
            {cid: self.conversations[cid] for cid in conversation_ids
             if cid in self.conversations}
            if conversation_ids
            else self.conversations
        )
        
        if format == "json":
            return {
                "conversations": [c.to_dict() for c in conversations.values()],
                "exported_at": time.time(),
                "total": len(conversations),
            }
        
        elif format == "markdown":
            md_content = []
            
            for conv in conversations.values():
                md_content.append(f"# Conversation {conv.id}")
                md_content.append(f"Created: {datetime.fromtimestamp(conv.created_at)}")
                
                if conv.summary:
                    md_content.append(f"\n## Summary\n{conv.summary}")
                
                if conv.topics:
                    md_content.append(f"\n## Topics\n{', '.join(conv.topics)}")
                
                md_content.append("\n## Messages\n")
                
                for msg in conv.messages:
                    timestamp = datetime.fromtimestamp(msg.timestamp)
                    md_content.append(f"\n**{msg.role.value.title()}** ({timestamp}):")
                    md_content.append(msg.content)
                
                md_content.append("\n---\n")
            
            return {
                "content": "\n".join(md_content),
                "format": "markdown",
                "total": len(conversations),
            }
        
        return {"error": f"Unknown format: {format}"}
    
    async def run(
        self,
        action: str,
        content: Optional[str] = None,
        role: str = "user",
        query: Optional[str] = None,
        conversation_id: Optional[str] = None,
        limit: int = 10,
        format: str = "json",
        **kwargs,
    ) -> MCPResourceDocument:
        """Execute memory action."""
        
        if action == "add":
            # Add message
            if not content:
                return MCPResourceDocument(data={"error": "Content required"})
            
            message = await self.add_message(role, content, kwargs.get("metadata"))
            
            return MCPResourceDocument(
                data={
                    "message_id": message.id,
                    "conversation_id": self.current_conversation_id,
                    "timestamp": message.timestamp,
                    "message_count": len(self.current_conversation.messages),
                }
            )
        
        elif action == "search":
            # Search messages
            if not query:
                return MCPResourceDocument(data={"error": "Query required"})
            
            results = await self.search_messages(
                query, limit, conversation_id, kwargs.get("role_filter")
            )
            
            return MCPResourceDocument(
                data={
                    "query": query,
                    "results": [
                        {
                            "message_id": msg.id,
                            "conversation_id": cid,
                            "role": msg.role.value,
                            "content": msg.content[:200],
                            "similarity": float(score),
                            "timestamp": msg.timestamp,
                        }
                        for msg, score, cid in results
                    ],
                    "total": len(results),
                }
            )
        
        elif action == "recall":
            # Recall conversation
            conv = self.conversations.get(
                conversation_id or self.current_conversation_id
            )
            
            if not conv:
                return MCPResourceDocument(
                    data={"error": f"Conversation not found: {conversation_id}"}
                )
            
            return MCPResourceDocument(data=conv.to_dict())
        
        elif action == "summarize":
            # Summarize conversation
            summary = await self.summarize_conversation(conversation_id)
            
            return MCPResourceDocument(
                data={
                    "conversation_id": conversation_id or self.current_conversation_id,
                    "summary": summary,
                }
            )
        
        elif action == "topics":
            # Extract topics
            topics = await self.extract_topics(conversation_id)
            
            return MCPResourceDocument(
                data={
                    "conversation_id": conversation_id or self.current_conversation_id,
                    "topics": topics,
                }
            )
        
        elif action == "export":
            # Export conversations
            result = self.export_conversations(
                format, kwargs.get("conversation_ids")
            )
            
            return MCPResourceDocument(data=result)
        
        elif action == "stats":
            # Get statistics
            stats = self.get_statistics()
            
            return MCPResourceDocument(data=stats)
        
        elif action == "new":
            # Start new conversation
            self.current_conversation_id = self._generate_conversation_id()
            self.current_conversation = Conversation(id=self.current_conversation_id)
            self.conversations[self.current_conversation_id] = self.current_conversation
            
            return MCPResourceDocument(
                data={
                    "conversation_id": self.current_conversation_id,
                    "created": True,
                }
            )
        
        else:
            return MCPResourceDocument(
                data={
                    "error": f"Unknown action: {action}",
                    "valid_actions": [
                        "add", "search", "recall", "summarize",
                        "topics", "export", "stats", "new"
                    ],
                }
            )
    
    async def call(self, **kwargs) -> str:
        """Tool interface for MCP."""
        result = await self.run(**kwargs)
        return result.to_json_string()


# Factory function
def create_conversation_memory(storage_path: Optional[str] = None):
    """Create conversation memory tool."""
    return ConversationMemory(storage_path)
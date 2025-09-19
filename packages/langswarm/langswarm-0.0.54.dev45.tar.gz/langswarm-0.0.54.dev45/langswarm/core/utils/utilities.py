import hashlib
import uuid
import os
import logging

#%pip install --upgrade tiktoken
import tiktoken

try:
    from transformers import GPT2Tokenizer
except ImportError:
    GPT2Tokenizer = None
    
from .misc import StripTags
from .subutilities.formatting import Formatting

logger = logging.getLogger(__name__)

class Utils(Formatting):
    def __init__(self):
        self.gpt2_tokenizer = None
        
        # Check if HuggingFace tokenizer should be disabled
        disable_hf = os.getenv('LANGSWARM_DISABLE_HF_TOKENIZER', '').lower() == 'true'
        if disable_hf:
            logger.info("🚫 HuggingFace tokenizer loading disabled via LANGSWARM_DISABLE_HF_TOKENIZER")
        elif not GPT2Tokenizer:
            logger.info("GPT2Tokenizer not available, using tiktoken fallback only")
        else:
            # Quick connectivity check to avoid rate limiting
            try:
                import requests
                # Quick HEAD request to check HuggingFace accessibility
                response = requests.head("https://huggingface.co", timeout=2)
                if response.status_code == 429:
                    logger.info("⚠️ HuggingFace rate limited, skipping tokenizer loading")
                    self.gpt2_tokenizer = None
                elif response.status_code >= 400:
                    logger.info(f"⚠️ HuggingFace not accessible (HTTP {response.status_code}), skipping tokenizer loading")
                    self.gpt2_tokenizer = None
                else:
                    # HuggingFace seems accessible, try loading tokenizer
                    logger.info("Loading GPT2 tokenizer...")
                    self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                    logger.info("✅ GPT2 tokenizer loaded successfully")
            except requests.RequestException:
                logger.info("⚠️ Network connectivity issue, skipping HuggingFace tokenizer")
                self.gpt2_tokenizer = None
            except Exception as e:
                logger.info(f"⚠️ Skipping GPT2 tokenizer due to: {e}")
                logger.info("🔄 Will use tiktoken fallback for all tokenization")
                self.gpt2_tokenizer = None
        
        self.bot_logs = []

    def _get_api_key(self, provider, api_key):
        """
        Retrieve the API key from environment variables or fallback to the provided key.

        Args:
            provider (str): LLM provider.
            api_key (str): Provided API key.

        Returns:
            str: Resolved API key.
        """
        env_var_map = {
            "langchain": "OPENAI_API_KEY",
            "langchain-openai": "OPENAI_API_KEY",
            "langchain-anthropic": "ANTHROPIC_API_KEY",
            "langchain-cohere": "COHERE_API_KEY",
            "langchain-google-palm": "GOOGLE_CLOUD_API_KEY",
            "langchain-azure-openai": "AZURE_OPENAI_API_KEY",
            "langchain-writer": "WRITER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_PALM_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_var = env_var_map.get(provider.lower())

        if env_var and (key_from_env := os.getenv(env_var)):
            return key_from_env

        if api_key:
            return api_key

        raise ValueError(f"API key for {provider} not found. Set {env_var} or pass the key explicitly.")
        
    def bot_log(self, bot, message):
        self.bot_logs.append((bot, message))

    def price_tokens_from_string(self, string, encoding_name="gpt-4-1106-preview", price_per_million=1, verbose=False):
        """
        Returns the number of tokens in a text string and its estimated price.
        
        Uses tiktoken as the primary tokenizer and GPT2Tokenizer as a fallback.
        """
        encoding_name = encoding_name or "gpt-4-1106-preview"
        try:
            # Attempt to use tiktoken for tokenization
            encoding = tiktoken.encoding_for_model(encoding_name)
            num_tokens = len(encoding.encode(string))
        except Exception:
            if verbose:
                print("tiktoken failed, falling back to GPT2Tokenizer.")
            # Fallback to GPT2Tokenizer
            if GPT2Tokenizer:
                num_tokens = len(self.gpt2_tokenizer.encode(string))
            else:
                print("No token counter found, install tiktoken or GPT2Tokenizer to get correct token count.")
                num_tokens = len(string)

        # Calculate price
        price = round(num_tokens * price_per_million / 1000000, 4)

        if verbose:
            print("Estimated tokens:", num_tokens)
            print("Estimated price: $", price)
        
        return num_tokens, price
    
    def truncate_text_to_tokens(self, text, max_tokens, tokenizer_name="gpt2", current_conversation="", verbose=False):
        """
        Truncate text to fit within the allowed number of tokens.

        Args:
            text (str): The input text to truncate.
            max_tokens (int): The maximum allowed number of tokens.
            tokenizer_name (str): The name of the tokenizer to use (default: "gpt2").

        Returns:
            str: The truncated text that fits within the token limit.
        """
        tokenizer_name = tokenizer_name or "gpt2"
        try:
            # Attempt to use tiktoken for tokenization
            tokenizer = tiktoken.encoding_for_model(tokenizer_name)
            # Tokenize the text
            tokens = tokenizer.encode(text)
            current_tokens = len(tokenizer.encode(current_conversation))
        except Exception:
            if verbose:
                print("tiktoken failed, falling back to GPT2Tokenizer.")
            # Use pre-loaded tokenizer (with backoff) or fallback
            if self.gpt2_tokenizer is not None:
                # Tokenize the text using the pre-loaded tokenizer
                tokens = self.gpt2_tokenizer.encode(text)
                current_tokens = len(self.gpt2_tokenizer.encode(current_conversation))
            else:
                if verbose:
                    print("No tokenizer available, returning original text.")
                return text
            
        # Check if any space is left?
        max_remaining_tokens = max_tokens - current_tokens
        
        if max_remaining_tokens <= 0:
            return text

        # Truncate tokens to the allowed limit
        truncated_tokens = tokens[:max_remaining_tokens]

        try:
            # Decode the truncated tokens back into text
            truncated_text = tokenizer.decode(truncated_tokens)
        except Exception:
            # Decode the truncated tokens back into text
            truncated_text = tokenizer.decode(truncated_tokens, skip_special_tokens=True)

        return truncated_text

    def generate_short_uuid(self, length = 8):
        # Generate a UUID and return a shortened version (min. 2 characters)
        return 'z'+str(uuid.uuid4())[:max(1,length-1)]
    
    def generate_md5_hash(self, query):
        return hashlib.md5(str(query).encode('utf-8')).hexdigest()

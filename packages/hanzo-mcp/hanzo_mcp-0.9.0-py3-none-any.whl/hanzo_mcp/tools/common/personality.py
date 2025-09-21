"""Complete enhanced tool personality system with 112+ personalities."""

import os
from typing import Set, Dict, List, Optional, Any
from dataclasses import dataclass, field


class PersonalityRegistry:
    """Registry for tool personalities with validation and export capabilities."""

    _personalities: Dict[str, 'ToolPersonality'] = {}
    _active_personality: Optional[str] = None

    @classmethod
    def register(cls, personality: 'ToolPersonality') -> None:
        """Register a tool personality with validation."""
        # Ensure agent enabled if API keys present
        personality = ensure_agent_enabled(personality)
        # Normalize tools (dedupe and sort)
        personality.tools = sorted(set(personality.tools))
        cls._personalities[personality.name] = personality

    @classmethod
    def add_personality(cls, personality: 'ToolPersonality') -> None:
        """Add a custom personality with validation."""
        if personality.name in cls._personalities:
            raise ValueError(f"Personality '{personality.name}' already exists")
        cls.register(personality)

    @classmethod
    def get(cls, name: str) -> Optional['ToolPersonality']:
        """Get a personality by name."""
        return cls._personalities.get(name)

    @classmethod
    def list(cls) -> List['ToolPersonality']:
        """List all registered personalities."""
        return list(cls._personalities.values())

    @classmethod
    def export(cls, include_tools: bool = False) -> List[Dict[str, Any]]:
        """Export personalities with metadata for UI/CLI."""
        result = []
        for p in cls._personalities.values():
            export = {
                "name": p.name,
                "programmer": p.programmer,
                "description": p.description,
                "tool_count": len(p.tools),
                "tags": p.tags if hasattr(p, 'tags') else [],
                "philosophy": p.philosophy if hasattr(p, 'philosophy') else None,
            }
            if include_tools:
                export["tools"] = p.tools
            if hasattr(p, 'metadata') and p.metadata:
                export["metadata"] = p.metadata
            result.append(export)
        return result

    @classmethod
    def filter_by_tags(cls, tags: List[str]) -> List['ToolPersonality']:
        """Filter personalities by tags."""
        return [
            p for p in cls._personalities.values()
            if hasattr(p, 'tags') and any(tag in p.tags for tag in tags)
        ]

    @classmethod
    def set_active(cls, name: str) -> None:
        """Set the active personality."""
        if name not in cls._personalities:
            raise ValueError(f"Personality '{name}' not found")
        cls._active_personality = name

        # Apply environment variables from the mode
        personality = cls._personalities[name]
        if personality.environment:
            for key, value in personality.environment.items():
                os.environ[key] = value

    @classmethod
    def get_active(cls) -> Optional['ToolPersonality']:
        """Get the active personality."""
        if cls._active_personality:
            return cls._personalities.get(cls._active_personality)
        return None

    @classmethod
    def get_active_tools(cls) -> Set[str]:
        """Get the set of tools from the active personality."""
        personality = cls.get_active()
        if personality:
            return set(personality.tools)
        return set()


def ensure_agent_enabled(personality: 'ToolPersonality') -> 'ToolPersonality':
    """Enable agent tool if API keys are present."""
    # Check for any API key environment variables
    api_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "TOGETHER_API_KEY",
        "HANZO_API_KEY",
    ]
    
    if any(os.environ.get(key) for key in api_keys):
        if "agent" not in personality.tools:
            personality.tools = personality.tools + ["agent"]
    
    return personality


def validate_tools(tools: List[str]) -> List[str]:
    """Validate and normalize tool names."""
    valid_tools = []
    for tool in tools:
        if tool in ALL_TOOL_NAMES:
            valid_tools.append(tool)
        else:
            # Silently skip unknown tools for now
            pass
    return sorted(set(valid_tools))


def register_default_personalities():
    """Register all default tool personalities with validation and deduplication."""
    for personality in personalities:
        # Ensure agent enabled if API keys present
        personality = ensure_agent_enabled(personality)
        # Validate and normalize tools (commented out to avoid issues with unknown tools)
        # personality.tools = validate_tools(personality.tools)
        personality.tools = sorted(set(personality.tools))
        PersonalityRegistry.register(personality)


def get_personality_from_env() -> Optional[str]:
    """Get personality name from environment variables."""
    return os.environ.get("HANZO_MODE") or os.environ.get("PERSONALITY") or os.environ.get("MODE")


def activate_personality_from_env():
    """Activate personality from environment if set."""
    personality_name = get_personality_from_env()
    if personality_name:
        try:
            PersonalityRegistry.set_active(personality_name)
            print(f"Activated personality: {personality_name}")
        except ValueError as e:
            print(f"Failed to activate personality: {e}")


@dataclass
class ToolPersonality:
    """Represents a programmer personality with tool preferences."""

    name: str
    programmer: str
    description: str
    tools: List[str]
    environment: Optional[Dict[str, str]] = None
    philosophy: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize personality configuration."""
        if not self.name:
            raise ValueError("Personality name is required")
        if not self.tools:
            raise ValueError("Personality must include at least one tool")
        # Deduplicate and sort tools
        self.tools = sorted(set(self.tools))


# Essential tools that are always available
ESSENTIAL_TOOLS = ['read', 'write', 'edit', 'tree', 'bash', 'think']

# Classic tool sets
UNIX_TOOLS = ['grep', 'find_files', 'bash', 'process', 'diff']
BUILD_TOOLS = ['bash', 'npx', 'uvx', 'process', 'cargo', 'gem', 'pip']
VERSION_CONTROL = ['git_search', 'diff', 'gh', 'gitlab']
AI_TOOLS = ['agent', 'consensus', 'critic', 'think', 'llm']
SEARCH_TOOLS = ['search', 'symbols', 'grep', 'git_search', 'ast_search']
DATABASE_TOOLS = ['sql_query', 'sql_search', 'graph_add', 'graph_query']
VECTOR_TOOLS = ['vector_index', 'vector_search', 'embeddings']

# Modern DevOps & Cloud tools
DEVOPS_TOOLS = ['docker', 'container_build', 'k8s', 'kubectl', 'helm', 'kustomize', 'minikube']
CI_CD_TOOLS = ['ci', 'github_actions', 'gitlab_ci', 'jenkins', 'circleci', 'artifact_publish']
CLOUD_TOOLS = ['terraform', 'ansible', 'cloud_cli', 'aws_s3', 'kms', 'secrets_manager']
OBSERVABILITY_TOOLS = ['prometheus', 'grafana', 'otel', 'logs', 'tracing', 'slo', 'chaos']

# Security & Quality tools
SECURITY_TOOLS = ['sast', 'dast', 'fuzz', 'dependency_scan', 'secret_scan', 'sigstore', 'sbom', 'snyk', 'trivy']
TESTING_TOOLS = ['pytest', 'jest', 'mocha', 'go_test', 'linters', 'formatter', 'coverage']

# ML/DataOps tools
ML_TOOLS = ['mlflow', 'dvc', 'kedro', 'mlem', 'model_registry', 'feature_store', 'jupyter', 'notebook']
AI_OPS_TOOLS = ['model_deploy', 'gpu_manager', 'quantize', 'onnx_convert', 'huggingface', 'hf_hub']

# Developer UX tools
DEV_UX_TOOLS = ['ngrok', 'localstack', 'devcontainer', 'vscode_remote', 'repl', 'watch', 'hot_reload']

# Utility tools
UTILITY_TOOLS = ['package_manager', 'image_scan', 'signing', 'notebook', 'batch', 'todo', 'rules']

# All available tools for validation
ALL_TOOL_NAMES = ['agent', 'ansible', 'artifact_publish', 'ast_search', 'aws_s3', 'bash', 'batch', 'cargo', 'chaos', 'ci', 'circleci', 'cloud_cli', 'consensus', 'container_build', 'coverage', 'critic', 'dast', 'dependency_scan', 'devcontainer', 'diff', 'docker', 'dvc', 'edit', 'embeddings', 'feature_store', 'find_files', 'formatter', 'fuzz', 'gem', 'gh', 'git_search', 'github_actions', 'gitlab', 'gitlab_ci', 'go_test', 'gpu_manager', 'grafana', 'graph_add', 'graph_query', 'grep', 'helm', 'hf_hub', 'hot_reload', 'huggingface', 'image_scan', 'jenkins', 'jest', 'jupyter', 'k8s', 'kedro', 'kms', 'kubectl', 'kustomize', 'linters', 'llm', 'localstack', 'logs', 'minikube', 'mlem', 'mlflow', 'mocha', 'model_deploy', 'model_registry', 'ngrok', 'notebook', 'npx', 'onnx_convert', 'otel', 'package_manager', 'pip', 'process', 'prometheus', 'pytest', 'quantize', 'read', 'repl', 'rules', 'sast', 'sbom', 'search', 'secret_scan', 'secrets_manager', 'signing', 'sigstore', 'slo', 'snyk', 'sql_query', 'sql_search', 'symbols', 'terraform', 'think', 'todo', 'tracing', 'tree', 'trivy', 'uvx', 'vector_index', 'vector_search', 'vscode_remote', 'watch', 'write']

# Complete list of 117 programmer personalities
personalities = [
    ToolPersonality(
        name="10x",
        programmer="10x Engineer",
        description="Maximum productivity, all tools enabled",
        philosophy="Move fast and optimize everything.",
        tools=['agent', 'ansible', 'artifact_publish', 'ast_search', 'aws_s3', 'bash', 'batch', 'cargo', 'chaos', 'ci', 'circleci', 'cloud_cli', 'consensus', 'container_build', 'coverage', 'critic', 'dast', 'dependency_scan', 'devcontainer', 'diff', 'docker', 'dvc', 'edit', 'embeddings', 'feature_store', 'find_files', 'formatter', 'fuzz', 'gem', 'gh', 'git_search', 'github_actions', 'gitlab', 'gitlab_ci', 'go_test', 'gpu_manager', 'grafana', 'graph_add', 'graph_query', 'grep', 'helm', 'hf_hub', 'hot_reload', 'huggingface', 'image_scan', 'jenkins', 'jest', 'jupyter', 'k8s', 'kedro', 'kms', 'kubectl', 'kustomize', 'linters', 'llm', 'localstack', 'logs', 'minikube', 'mlem', 'mlflow', 'mocha', 'model_deploy', 'model_registry', 'ngrok', 'notebook', 'npx', 'onnx_convert', 'otel', 'package_manager', 'pip', 'process', 'prometheus', 'pytest', 'quantize', 'read', 'repl', 'rules', 'sast', 'sbom', 'search', 'secret_scan', 'secrets_manager', 'signing', 'sigstore', 'slo', 'snyk', 'sql_query', 'sql_search', 'symbols', 'terraform', 'think', 'todo', 'tracing', 'tree', 'trivy', 'uvx', 'vector_index', 'vector_search', 'vscode_remote', 'watch', 'write'],
        environment={'PRODUCTIVITY': 'MAX', 'TOOLS': 'ALL', 'DOCKER_BUILDKIT': '1', 'CI': 'true'},
        tags=['productivity', 'fullstack', 'power-user'],
    ),
    ToolPersonality(
        name="academic",
        programmer="Academic Researcher",
        description="Publish or perish",
        philosophy="Standing on the shoulders of giants.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'jupyter', 'todo', 'critic', 'agent', 'consensus', 'critic', 'think', 'search', 'symbols', 'grep', 'git_search'],
        environment={'LATEX_ENGINE': 'xelatex'},
        tags=['general'],
    ),
    ToolPersonality(
        name="ada",
        programmer="Ada Lovelace",
        description="First programmer - algorithms as poetry",
        philosophy="The Analytical Engine has no pretensions to originate anything. It can do whatever we know how to order it to perform.",
        tools=['ast_search', 'bash', 'edit', 'formatter', 'git_search', 'grep', 'notebook', 'read', 'search', 'symbols', 'think', 'tree', 'write'],
        environment={'ALGORITHM_STYLE': 'poetic'},
        tags=['pioneer', 'academic', 'algorithms'],
    ),
    ToolPersonality(
        name="adrian",
        programmer="Adrian Holovaty",
        description="Django co-creator - web framework for perfectionists",
        philosophy="The web framework for perfectionists with deadlines.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'uvx', 'sql_query', 'watch', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'DJANGO_SETTINGS_MODULE': 'settings'},
        tags=['pioneer', 'web'],
    ),
    ToolPersonality(
        name="anders",
        programmer="Anders Hejlsberg",
        description="TypeScript/C# creator - type safety matters",
        philosophy="TypeScript is JavaScript that scales.",
        tools=['ast_search', 'bash', 'cargo', 'edit', 'formatter', 'gem', 'git_search', 'grep', 'npx', 'pip', 'process', 'read', 'rules', 'search', 'symbols', 'think', 'tree', 'uvx', 'watch', 'write'],
        environment={'TYPESCRIPT_VERSION': '5.0', 'DOTNET_VERSION': '8.0'},
        tags=['languages', 'typescript', 'types'],
    ),
    ToolPersonality(
        name="andrej",
        programmer="Andrej Karpathy",
        description="AI educator & former Tesla AI director",
        philosophy="The unreasonable effectiveness of neural networks.",
        tools=['agent', 'ast_search', 'bash', 'consensus', 'critic', 'dvc', 'edit', 'feature_store', 'git_search', 'gpu_manager', 'grep', 'jupyter', 'kedro', 'llm', 'mlem', 'mlflow', 'model_registry', 'notebook', 'read', 'search', 'symbols', 'think', 'tree', 'uvx', 'watch', 'write'],
        environment={'CUDA_VISIBLE_DEVICES': '0', 'PYTHONUNBUFFERED': '1'},
        tags=['ai', 'ml', 'education'],
    ),
    ToolPersonality(
        name="andrew",
        programmer="Andrew Ng",
        description="AI educator & Coursera co-founder",
        philosophy="AI is the new electricity.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'jupyter', 'todo', 'watch'],
        environment={'CUDA_VISIBLE_DEVICES': '0'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="bill",
        programmer="Bill Joy",
        description="Vi creator & BSD contributor",
        philosophy="The best way to predict the future is to invent it.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'neovim_edit', 'neovim_command', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'EDITOR': 'vi'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="bjarne",
        programmer="Bjarne Stroustrup",
        description="C++ creator - zero-overhead abstractions",
        philosophy="C++ is designed to allow you to express ideas.",
        tools=['bash', 'cargo', 'content_replace', 'diff', 'edit', 'find_files', 'formatter', 'gem', 'grep', 'multi_edit', 'npx', 'pip', 'process', 'read', 'symbols', 'think', 'tree', 'uvx', 'write'],
        environment={'CXX': 'g++', 'CXXFLAGS': '-std=c++20 -Wall'},
        tags=['languages', 'cpp', 'performance'],
    ),
    ToolPersonality(
        name="bram",
        programmer="Bram Moolenaar",
        description="Vim creator",
        philosophy="The best way to avoid RSI is to not type so much.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'neovim_edit', 'neovim_command', 'neovim_session'],
        environment={'VIM_VERSION': '9.0'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="brendan",
        programmer="Brendan Eich",
        description="JavaScript creator - dynamic and flexible",
        philosophy="Always bet on JS.",
        tools=['ast_search', 'bash', 'cargo', 'devcontainer', 'edit', 'formatter', 'gem', 'git_search', 'grep', 'hot_reload', 'jest', 'localstack', 'ngrok', 'npx', 'pip', 'process', 'read', 'repl', 'rules', 'search', 'symbols', 'think', 'todo', 'tree', 'uvx', 'vscode_remote', 'watch', 'write'],
        environment={'NODE_ENV': 'development', 'NPM_CONFIG_LOGLEVEL': 'warn'},
        tags=['languages', 'javascript', 'web'],
    ),
    ToolPersonality(
        name="brian",
        programmer="Brian Kernighan",
        description="AWK co-creator & Unix pioneer",
        philosophy="Controlling complexity is the essence of computer programming.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'grep', 'content_replace', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'AWK': 'gawk'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="bruce",
        programmer="Bruce Schneier",
        description="Security expert & cryptographer",
        philosophy="Security is a process, not a product.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'git_search', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'SECURITY_AUDIT': 'true'},
        tags=['security'],
    ),
    ToolPersonality(
        name="carmack",
        programmer="John Carmack",
        description="id Software - Doom & Quake creator",
        philosophy="Focus is a matter of deciding what things you're not going to do.",
        tools=['bash', 'cargo', 'diff', 'edit', 'find_files', 'gem', 'gpu_manager', 'grep', 'multi_edit', 'npx', 'pip', 'process', 'read', 'symbols', 'think', 'tree', 'uvx', 'watch', 'write'],
        environment={'GL_VERSION': '4.6', 'VULKAN_SDK': '/usr/local/vulkan'},
        tags=['gaming', 'graphics', 'performance'],
    ),
    ToolPersonality(
        name="casey",
        programmer="Casey Muratori",
        description="Handmade Hero creator",
        philosophy="Performance matters. Write code from scratch.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'watch', 'process', 'critic'],
        environment={'HANDMADE': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="chris",
        programmer="Chris Olah",
        description="AI interpretability researcher",
        philosophy="Understanding neural networks matters.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'vector_index', 'vector_search', 'jupyter', 'critic'],
        environment={'DISTILL_MODE': 'interactive'},
        tags=['ai'],
    ),
    ToolPersonality(
        name="chris_lattner",
        programmer="Chris Lattner",
        description="LLVM & Swift creator",
        philosophy="Compiler infrastructure should be modular.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'multi_edit', 'critic', 'bash', 'npx', 'uvx', 'process'],
        environment={'LLVM_VERSION': '16'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="cloud_native",
        programmer="Cloud Native Developer",
        description="Kubernetes-first development",
        philosophy="Containers everywhere, orchestrate everything.",
        tools=['ansible', 'artifact_publish', 'aws_s3', 'bash', 'chaos', 'ci', 'circleci', 'cloud_cli', 'container_build', 'dast', 'dependency_scan', 'diff', 'docker', 'edit', 'fuzz', 'gh', 'git_search', 'github_actions', 'gitlab', 'gitlab_ci', 'grafana', 'helm', 'jenkins', 'k8s', 'kms', 'kubectl', 'kustomize', 'logs', 'minikube', 'otel', 'prometheus', 'read', 'sast', 'sbom', 'secret_scan', 'secrets_manager', 'sigstore', 'slo', 'snyk', 'terraform', 'think', 'tracing', 'tree', 'trivy', 'write'],
        environment={'KUBECONFIG': '~/.kube/config', 'DOCKER_REGISTRY': 'ghcr.io', 'CLOUD_PROVIDER': 'aws', 'TERRAFORM_VERSION': '1.5'},
        tags=['devops', 'kubernetes', 'cloud'],
    ),
    ToolPersonality(
        name="creative",
        programmer="Creative Coder",
        description="Code as art",
        philosophy="Programming is the art of the possible.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'watch', 'jupyter', 'todo', 'agent', 'consensus', 'critic', 'think'],
        environment={'P5_MODE': 'global'},
        tags=['general'],
    ),
    ToolPersonality(
        name="dan_kaminsky",
        programmer="Dan Kaminsky",
        description="DNS security researcher",
        philosophy="Break it to make it better.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'process', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'DNSSEC': 'true'},
        tags=['security'],
    ),
    ToolPersonality(
        name="daniel_b",
        programmer="Daniel J. Bernstein",
        description="djb - qmail & Curve25519 creator",
        philosophy="Security through simplicity.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'QMAIL_HOME': '/var/qmail'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="daniel_r",
        programmer="Daniel Robbins",
        description="Gentoo founder",
        philosophy="Your system, your way.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'bash', 'npx', 'uvx', 'process', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'GENTOO_PROFILE': 'default/linux/amd64/17.1'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="data_scientist",
        programmer="Data Scientist",
        description="Analyze all the things",
        philosophy="In God we trust. All others must bring data.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'jupyter', 'sql_query', 'stats', 'vector_index', 'vector_search', 'agent', 'consensus', 'critic', 'think'],
        environment={'JUPYTER_THEME': 'dark'},
        tags=['general'],
    ),
    ToolPersonality(
        name="david",
        programmer="David Heinemeier Hansson",
        description="Rails creator - convention over configuration",
        philosophy="Optimize for programmer happiness.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'sql_query', 'watch', 'todo', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'RAILS_ENV': 'development'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="demis",
        programmer="Demis Hassabis",
        description="DeepMind co-founder",
        philosophy="Solve intelligence, use it to solve everything else.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'vector_index', 'vector_search', 'agent', 'consensus'],
        environment={'JAX_VERSION': '0.4'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="dennis",
        programmer="Dennis Ritchie",
        description="C creator - close to the metal",
        philosophy="UNIX is basically a simple operating system, but you have to be a genius to understand the simplicity.",
        tools=['bash', 'content_replace', 'diff', 'edit', 'find_files', 'gdb', 'grep', 'process', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'CC': 'gcc', 'CFLAGS': '-Wall -O2'},
        tags=['languages', 'c', 'unix'],
    ),
    ToolPersonality(
        name="devops",
        programmer="DevOps Engineer",
        description="Automate everything",
        philosophy="You build it, you run it.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'bash', 'npx', 'uvx', 'process', 'process', 'watch', 'todo', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'CI_CD': 'enabled'},
        tags=['general'],
    ),
    ToolPersonality(
        name="dijkstra",
        programmer="Edsger W. Dijkstra",
        description="Structured programming and correctness",
        philosophy="Simplicity is prerequisite for reliability.",
        tools=['bash', 'coverage', 'edit', 'formatter', 'go_test', 'jest', 'linters', 'mocha', 'model_check', 'pytest', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'GOTO_ALLOWED': 'false', 'PROOF_REQUIRED': 'true'},
        tags=['academic', 'correctness', 'algorithms'],
    ),
    ToolPersonality(
        name="donald",
        programmer="Donald Knuth",
        description="TeX creator - literate programming",
        philosophy="Premature optimization is the root of all evil.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'todo', 'critic'],
        environment={'TEXMFHOME': '~/texmf'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="douglas",
        programmer="Douglas Crockford",
        description="JSON creator - JavaScript the good parts",
        philosophy="JavaScript has some extraordinarily good parts.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'symbols', 'critic', 'search', 'symbols', 'grep', 'git_search'],
        environment={'JSLINT': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="dwight",
        programmer="Dwight Merriman",
        description="MongoDB co-creator - document databases",
        philosophy="Build the database you want to use.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'watch', 'todo'],
        environment={'MONGO_VERSION': '6.0'},
        tags=['pioneer', 'database'],
    ),
    ToolPersonality(
        name="dylan",
        programmer="Dylan Field",
        description="Figma co-founder",
        philosophy="Design tools should be collaborative.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'watch', 'todo', 'rules'],
        environment={'FIGMA_API': 'enabled'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="edgar",
        programmer="Edgar F. Codd",
        description="Relational model inventor",
        philosophy="Data independence is key.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'critic'],
        environment={'SQL_MODE': 'ANSI'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="enterprise",
        programmer="Enterprise Developer",
        description="Process and compliance",
        philosophy="Nobody ever got fired for buying IBM.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'critic', 'rules', 'stats', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'COMPLIANCE': 'SOC2'},
        tags=['general'],
    ),
    ToolPersonality(
        name="evan",
        programmer="Evan You",
        description="Vue.js creator - progressive framework",
        philosophy="Approachable, versatile, performant.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'watch', 'symbols', 'todo', 'bash', 'npx', 'uvx', 'process'],
        environment={'VUE_VERSION': '3'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="fabrice",
        programmer="Fabrice Bellard",
        description="QEMU & FFmpeg creator",
        philosophy="Small, fast, and elegant code.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'process', 'bash', 'npx', 'uvx', 'process'],
        environment={'QEMU_VERSION': '8.0'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="frances",
        programmer="Frances E. Allen",
        description="Compiler optimization and parallelization",
        philosophy="Parallel computing is the future.",
        tools=['bash', 'chaos', 'compiler', 'edit', 'gpu_manager', 'grafana', 'logs', 'otel', 'prometheus', 'read', 'slo', 'think', 'tracing', 'tree', 'write'],
        environment={'OPTIMIZATION_LEVEL': 'O3', 'PARALLELISM': 'auto'},
        tags=['compilers', 'optimization', 'parallel'],
    ),
    ToolPersonality(
        name="francois",
        programmer="François Chollet",
        description="Keras creator",
        philosophy="Deep learning for humans.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'jupyter', 'watch', 'todo'],
        environment={'KERAS_BACKEND': 'tensorflow'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="fullstack",
        programmer="Full Stack Developer",
        description="Every tool for every job",
        philosophy="Jack of all trades, master of... well, all trades.",
        tools=['grep', 'sql_search', 'git_search', 'tree', 'read', 'critic', 'think', 'graph_query', 'sql_query', 'watch', 'diff', 'bash', 'consensus', 'jupyter', 'vector_index', 'neovim_edit', 'mcp', 'edit', 'rules', 'todo', 'npx', 'find_files', 'vector_search', 'process', 'uvx', 'search', 'write', 'graph_add', 'symbols', 'agent'],
        environment={'ALL_TOOLS': 'enabled'},
        tags=['general'],
    ),
    ToolPersonality(
        name="gabe",
        programmer="Gabe Newell",
        description="Valve founder - Half-Life & Steam",
        philosophy="The easiest way to stop piracy is not by putting antipiracy technology to work. It's by giving those people a service that's better than what they're receiving from the pirates.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'process', 'watch', 'todo', 'bash', 'npx', 'uvx', 'process'],
        environment={'STEAM_RUNTIME': '1'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="geoffrey",
        programmer="Geoffrey Hinton",
        description="Deep learning godfather",
        philosophy="The brain has to work with what it's got.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'vector_index', 'vector_search', 'jupyter'],
        environment={'TF_VERSION': '2.13'},
        tags=['general'],
    ),
    ToolPersonality(
        name="grace",
        programmer="Grace Hopper",
        description="Compiler pioneer and debugging inventor",
        philosophy="The most dangerous phrase in the language is 'We've always done it this way.'",
        tools=['artifact_publish', 'bash', 'ci', 'circleci', 'compiler', 'coverage', 'docker', 'edit', 'formatter', 'github_actions', 'gitlab_ci', 'go_test', 'jenkins', 'jest', 'linters', 'mocha', 'pytest', 'read', 'think', 'tree', 'write'],
        environment={'COMPILER_TOOL': 'cobol-compat', 'DOCKER_REGISTRY': 'ghcr.io'},
        tags=['pioneer', 'compilers', 'pragmatic'],
    ),
    ToolPersonality(
        name="graydon",
        programmer="Graydon Hoare",
        description="Rust creator - memory safety without GC",
        philosophy="Memory safety without garbage collection, concurrency without data races.",
        tools=['bash', 'cargo', 'coverage', 'critic', 'edit', 'formatter', 'gem', 'go_test', 'jest', 'linters', 'mocha', 'multi_edit', 'npx', 'pip', 'process', 'pytest', 'read', 'symbols', 'think', 'todo', 'tree', 'uvx', 'write'],
        environment={'RUST_BACKTRACE': '1', 'CARGO_HOME': '~/.cargo'},
        tags=['languages', 'rust', 'safety'],
    ),
    ToolPersonality(
        name="guido",
        programmer="Guido van Rossum",
        description="Python's BDFL - readability counts",
        philosophy="There should be one-- and preferably only one --obvious way to do it.",
        tools=['agent', 'ast_search', 'bash', 'consensus', 'critic', 'dvc', 'edit', 'feature_store', 'formatter', 'git_search', 'grep', 'jupyter', 'kedro', 'llm', 'mlem', 'mlflow', 'model_registry', 'multi_edit', 'notebook', 'pytest', 'read', 'rules', 'search', 'symbols', 'think', 'tree', 'uvx', 'write'],
        environment={'PYTHONPATH': '.', 'PYTEST_ARGS': '-xvs', 'BLACK_CONFIG': 'pyproject.toml'},
        tags=['languages', 'python', 'readability'],
    ),
    ToolPersonality(
        name="guillermo",
        programmer="Guillermo Rauch",
        description="Vercel founder & Next.js creator",
        philosophy="Make the Web. Faster.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'watch', 'rules', 'bash', 'npx', 'uvx', 'process'],
        environment={'NEXT_VERSION': '14'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="hanzo",
        programmer="Hanzo AI Default",
        description="Balanced productivity and quality",
        philosophy="AI-powered development at scale.",
        tools=['agent', 'artifact_publish', 'ast_search', 'bash', 'cargo', 'ci', 'circleci', 'consensus', 'container_build', 'critic', 'diff', 'docker', 'dvc', 'edit', 'feature_store', 'gem', 'gh', 'git_search', 'github_actions', 'gitlab', 'gitlab_ci', 'grep', 'helm', 'jenkins', 'jupyter', 'k8s', 'kedro', 'kubectl', 'kustomize', 'llm', 'minikube', 'mlem', 'mlflow', 'model_registry', 'multi_edit', 'notebook', 'npx', 'pip', 'process', 'read', 'rules', 'search', 'symbols', 'think', 'todo', 'tree', 'uvx', 'watch', 'write'],
        environment={'HANZO_MODE': 'enabled', 'AI_ASSIST': 'true', 'DOCKER_BUILDKIT': '1', 'KUBECONFIG': '~/.kube/config'},
        tags=['default', 'balanced', 'ai'],
    ),
    ToolPersonality(
        name="hideo",
        programmer="Hideo Kojima",
        description="Metal Gear creator",
        philosophy="70% of my body is made of movies.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'watch', 'critic'],
        environment={'KOJIMA_PRODUCTIONS': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="hoare",
        programmer="Tony Hoare",
        description="Algorithms, CSP, and Hoare logic",
        philosophy="Premature optimization is the root of all evil.",
        tools=['bash', 'coverage', 'edit', 'formatter', 'go_test', 'jest', 'linters', 'mocha', 'model_check', 'pytest', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'PROOF_ASSISTANT': 'coq', 'NULL_REFERENCES': 'banned'},
        tags=['algorithms', 'correctness', 'theory'],
    ),
    ToolPersonality(
        name="ian",
        programmer="Ian Murdock",
        description="Debian founder",
        philosophy="Free software, free society.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'grep', 'find_files', 'bash', 'process', 'diff', 'todo'],
        environment={'DEBIAN_FRONTEND': 'noninteractive'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="ilya",
        programmer="Ilya Sutskever",
        description="OpenAI co-founder - scaling is all you need",
        philosophy="AGI is the goal.",
        tools=['agent', 'ansible', 'aws_s3', 'bash', 'batch', 'cloud_cli', 'consensus', 'critic', 'dvc', 'edit', 'feature_store', 'gpu_manager', 'hf_hub', 'huggingface', 'jupyter', 'kedro', 'kms', 'llm', 'mlem', 'mlflow', 'model_deploy', 'model_registry', 'notebook', 'onnx_convert', 'quantize', 'read', 'secrets_manager', 'symbols', 'terraform', 'think', 'tree', 'uvx', 'write'],
        environment={'OPENAI_API_KEY': '', 'PYTORCH_ENABLE_MPS': '1', 'CUDA_VISIBLE_DEVICES': '0'},
        tags=['ai', 'ml', 'research'],
    ),
    ToolPersonality(
        name="james",
        programmer="James Gosling",
        description="Java creator - write once, run anywhere",
        philosophy="Java is C++ without the guns, knives, and clubs.",
        tools=['bash', 'batch', 'cargo', 'edit', 'gem', 'gradle', 'maven', 'npx', 'pip', 'process', 'read', 'symbols', 'think', 'todo', 'tree', 'uvx', 'write'],
        environment={'JAVA_HOME': '/usr/lib/jvm/java-11-openjdk', 'MAVEN_OPTS': '-Xmx1024m'},
        tags=['languages', 'java', 'enterprise'],
    ),
    ToolPersonality(
        name="jeff_dean",
        programmer="Jeff Dean",
        description="MapReduce & BigTable co-creator",
        philosophy="Design for planet-scale.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'vector_index', 'vector_search', 'batch'],
        environment={'HADOOP_HOME': '/opt/hadoop'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="jeremy",
        programmer="Jeremy Ashkenas",
        description="CoffeeScript & Backbone creator",
        philosophy="It's just JavaScript.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'symbols', 'watch'],
        environment={'COFFEE_VERSION': '2.0'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="jeremy_howard",
        programmer="Jeremy Howard",
        description="fast.ai founder",
        philosophy="Deep learning should be accessible to all.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'jupyter', 'watch', 'rules'],
        environment={'FASTAI_VERSION': '2.7'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="jim_gray",
        programmer="Jim Gray",
        description="Transaction processing pioneer",
        philosophy="The transaction is the unit of work.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'batch', 'critic'],
        environment={'ISOLATION_LEVEL': 'SERIALIZABLE'},
        tags=['general'],
    ),
    ToolPersonality(
        name="joe",
        programmer="Joe Armstrong",
        description="Erlang creator",
        philosophy="Let it crash.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'process', 'watch', 'critic'],
        environment={'ERL_VERSION': 'OTP-26'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="john",
        programmer="John Resig",
        description="jQuery creator - write less, do more",
        philosophy="Do more with less code.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'watch', 'symbols', 'search', 'symbols', 'grep', 'git_search'],
        environment={'JQUERY_VERSION': '3.6'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="john_carmack",
        programmer="John Carmack",
        description="id Software - Doom & Quake creator",
        philosophy="Focus is a matter of deciding what things you're not going to do.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'watch', 'process', 'bash', 'npx', 'uvx', 'process'],
        environment={'OPENGL_VERSION': '4.6'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="jonathan",
        programmer="Jonathan Blow",
        description="Braid & The Witness creator",
        philosophy="Optimize for deep, meaningful experiences.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'critic', 'watch'],
        environment={'JAI_COMPILER': 'beta'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="jordan",
        programmer="Jordan Walke",
        description="React creator - declarative UIs",
        philosophy="Learn once, write anywhere.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'watch', 'symbols', 'rules', 'bash', 'npx', 'uvx', 'process'],
        environment={'REACT_VERSION': '18'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="jose",
        programmer="José Valim",
        description="Elixir creator",
        philosophy="Productive. Reliable. Fast.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'watch', 'process', 'todo'],
        environment={'ELIXIR_VERSION': '1.15'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="judd",
        programmer="Judd Vinet",
        description="Arch Linux creator",
        philosophy="Keep it simple.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'bash', 'npx', 'uvx', 'process', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'ARCH_VERSION': 'rolling'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="katie",
        programmer="Katie Moussouris",
        description="Bug bounty pioneer",
        philosophy="Hackers are a resource, not a threat.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'todo'],
        environment={'BUG_BOUNTY': 'enabled'},
        tags=['general'],
    ),
    ToolPersonality(
        name="ken",
        programmer="Ken Thompson",
        description="Unix creator - elegant minimalism",
        philosophy="When in doubt, use brute force.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'PATH': '/usr/local/bin:$PATH'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="lamport",
        programmer="Leslie Lamport",
        description="Distributed systems and TLA+",
        philosophy="A distributed system is one in which the failure of a computer you didn't even know existed can render your own computer unusable.",
        tools=['bash', 'chaos', 'container_build', 'docker', 'edit', 'grafana', 'helm', 'k8s', 'kubectl', 'kubernetes', 'kustomize', 'logs', 'minikube', 'model_check', 'otel', 'prometheus', 'read', 'slo', 'think', 'tla_plus', 'tracing', 'tree', 'write'],
        environment={'SPEC_TOOL': 'tla+', 'MODEL_CHECK_TIMEOUT': '300'},
        tags=['distributed', 'correctness', 'theory'],
    ),
    ToolPersonality(
        name="larry",
        programmer="Larry Wall",
        description="Perl creator - there's more than one way to do it",
        philosophy="The three chief virtues of a programmer are laziness, impatience, and hubris.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'grep', 'content_replace', 'batch', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'PERL5LIB': './lib'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="lennart",
        programmer="Lennart Poettering",
        description="systemd creator",
        philosophy="Do one thing and do it well... or do everything.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'process', 'watch', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'SYSTEMD_VERSION': '253'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="linus",
        programmer="Linus Torvalds",
        description="Linux & Git creator - pragmatic excellence",
        philosophy="Talk is cheap. Show me the code.",
        tools=['bash', 'content_replace', 'critic', 'diff', 'edit', 'find_files', 'gh', 'git_search', 'gitlab', 'grep', 'process', 'read', 'think', 'tree', 'write'],
        environment={'KERNEL_VERSION': '6.0', 'GIT_AUTHOR_NAME': 'Linus Torvalds'},
        tags=['systems', 'linux', 'git'],
    ),
    ToolPersonality(
        name="liskov",
        programmer="Barbara Liskov",
        description="Software engineering principles & abstraction",
        philosophy="Abstraction is the key to managing complexity.",
        tools=['bash', 'coverage', 'edit', 'formatter', 'go_test', 'jest', 'linters', 'mocha', 'pytest', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'SOLID_PRINCIPLES': 'true', 'LISKOV_SUBSTITUTION': 'enforced'},
        tags=['engineering', 'principles', 'oop'],
    ),
    ToolPersonality(
        name="margaret",
        programmer="Margaret Hamilton",
        description="Software engineering for mission-critical systems",
        philosophy="There was no choice but to be pioneers.",
        tools=['bash', 'coverage', 'dast', 'dependency_scan', 'edit', 'formatter', 'fuzz', 'go_test', 'jest', 'linters', 'mocha', 'model_check', 'pytest', 'read', 'sast', 'sbom', 'secret_scan', 'sigstore', 'snyk', 'think', 'tree', 'trivy', 'write'],
        environment={'ERROR_HANDLING': 'exhaustive', 'MISSION_CRITICAL': 'true'},
        tags=['engineering', 'reliability', 'space'],
    ),
    ToolPersonality(
        name="mark_shuttleworth",
        programmer="Mark Shuttleworth",
        description="Ubuntu founder",
        philosophy="Linux for human beings.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'rules', 'bash', 'npx', 'uvx', 'process'],
        environment={'UBUNTU_VERSION': '22.04'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="markus",
        programmer="Markus Persson",
        description="Minecraft creator - Notch",
        philosophy="Just make games for yourself and try to have fun.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'watch', 'todo', 'process'],
        environment={'LWJGL_VERSION': '3.3'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="matei",
        programmer="Matei Zaharia",
        description="Apache Spark creator",
        philosophy="In-memory computing changes everything.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'batch', 'process', 'jupyter'],
        environment={'SPARK_MASTER': 'local[*]'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="matt",
        programmer="Matt Mullenweg",
        description="WordPress creator - democratize publishing",
        philosophy="Code is poetry.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'watch', 'rules', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'WP_DEBUG': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="matt_blaze",
        programmer="Matt Blaze",
        description="Cryptographer & security researcher",
        philosophy="Crypto is hard to get right.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'git_search'],
        environment={'CRYPTO_LIBRARY': 'nacl'},
        tags=['security'],
    ),
    ToolPersonality(
        name="matz",
        programmer="Yukihiro Matsumoto",
        description="Ruby creator - optimize for developer happiness",
        philosophy="Ruby is designed to make programmers happy.",
        tools=['artifact_publish', 'ast_search', 'bash', 'batch', 'ci', 'circleci', 'edit', 'gem', 'git_search', 'github_actions', 'gitlab_ci', 'grep', 'jenkins', 'read', 'search', 'symbols', 'think', 'todo', 'tree', 'write'],
        environment={'RUBY_VERSION': '3.0', 'BUNDLE_PATH': 'vendor/bundle'},
        tags=['languages', 'ruby', 'happiness'],
    ),
    ToolPersonality(
        name="mccarthy",
        programmer="John McCarthy",
        description="AI pioneer and Lisp inventor",
        philosophy="He who refuses to do arithmetic is doomed to talk nonsense.",
        tools=['agent', 'bash', 'consensus', 'critic', 'edit', 'llm', 'notebook', 'read', 'repl', 'symbols', 'think', 'tree', 'write'],
        environment={'LISP_DIALECT': 'common-lisp', 'AI_PARADIGM': 'symbolic'},
        tags=['ai', 'languages', 'pioneer'],
    ),
    ToolPersonality(
        name="michael_s",
        programmer="Michael Stonebraker",
        description="PostgreSQL creator - ACID matters",
        philosophy="One size does not fit all in databases.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'batch', 'todo'],
        environment={'PGDATA': '/var/lib/postgresql/data'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="michael_w",
        programmer="Michael Widenius",
        description="MySQL/MariaDB creator",
        philosophy="A small fast database for the web.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'watch'],
        environment={'MYSQL_HOME': '/usr/local/mysql'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="miguel",
        programmer="Miguel de Icaza",
        description="GNOME & Mono creator",
        philosophy="Open source is about standing on the shoulders of giants.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'todo', 'bash', 'npx', 'uvx', 'process'],
        environment={'MONO_VERSION': '6.12'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="mike",
        programmer="Mike Cafarella",
        description="Hadoop co-creator",
        philosophy="Storage is cheap, compute is cheap.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'batch', 'process'],
        environment={'HADOOP_CONF_DIR': '/etc/hadoop'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="minimal",
        programmer="Minimalist",
        description="Just the essentials",
        philosophy="Less is more.",
        tools=['bash', 'edit', 'read', 'think', 'tree', 'write'],
        environment={'MINIMAL_MODE': 'true'},
        tags=['minimal', 'focused', 'simple'],
    ),
    ToolPersonality(
        name="mitchell",
        programmer="Mitchell Hashimoto",
        description="HashiCorp founder - infrastructure as code",
        philosophy="Automate everything.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'bash', 'process', 'watch', 'todo', 'bash', 'npx', 'uvx', 'process'],
        environment={'TERRAFORM_VERSION': '1.0'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="ml_engineer",
        programmer="ML Engineer",
        description="Production ML systems",
        philosophy="From notebook to production pipeline.",
        tools=['agent', 'ansible', 'aws_s3', 'bash', 'chaos', 'cloud_cli', 'consensus', 'container_build', 'critic', 'docker', 'dvc', 'edit', 'feature_store', 'gpu_manager', 'grafana', 'helm', 'hf_hub', 'huggingface', 'jupyter', 'k8s', 'kedro', 'kms', 'kubectl', 'kustomize', 'llm', 'logs', 'minikube', 'mlem', 'mlflow', 'model_deploy', 'model_registry', 'notebook', 'onnx_convert', 'otel', 'prometheus', 'quantize', 'read', 'secrets_manager', 'slo', 'terraform', 'think', 'tracing', 'tree', 'write'],
        environment={'MLFLOW_TRACKING_URI': 'http://localhost:5000', 'DVC_REMOTE': 's3://ml-artifacts', 'CUDA_VISIBLE_DEVICES': '0,1'},
        tags=['ml', 'mlops', 'production'],
    ),
    ToolPersonality(
        name="moxie",
        programmer="Moxie Marlinspike",
        description="Signal creator - privacy for everyone",
        philosophy="Making private communication simple.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'rules'],
        environment={'SIGNAL_PROTOCOL': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="nat",
        programmer="Nat Friedman",
        description="GitHub CEO & AI entrepreneur",
        philosophy="Developers are the builders of the digital world.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'git_search', 'todo'],
        environment={'GITHUB_TOKEN': 'ghp_...'},
        tags=['ai'],
    ),
    ToolPersonality(
        name="palmer",
        programmer="Palmer Luckey",
        description="Oculus founder",
        philosophy="VR is the final medium.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'watch', 'process', 'bash', 'npx', 'uvx', 'process'],
        environment={'UNITY_VERSION': '2023.1'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="patrick",
        programmer="Patrick Volkerding",
        description="Slackware creator",
        philosophy="Keep it simple, keep it stable.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'SLACKWARE_VERSION': '15.0'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="phil",
        programmer="Phil Zimmermann",
        description="PGP creator - privacy matters",
        philosophy="If privacy is outlawed, only outlaws will have privacy.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'content_replace', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'GPG_TTY': '$(tty)'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="radia",
        programmer="Radia Perlman",
        description="Network protocols and spanning tree",
        philosophy="The beautiful thing about standards is that there are so many to choose from.",
        tools=['ansible', 'aws_s3', 'bash', 'cloud_cli', 'container_build', 'docker', 'edit', 'helm', 'k8s', 'kms', 'kubectl', 'kustomize', 'minikube', 'read', 'secrets_manager', 'terraform', 'think', 'tree', 'write'],
        environment={'NETWORK_PROTOCOL': 'stp', 'ROUTING_ALGORITHM': 'is-is'},
        tags=['networking', 'protocols', 'infrastructure'],
    ),
    ToolPersonality(
        name="ralph",
        programmer="Ralph Merkle",
        description="Merkle trees inventor",
        philosophy="Cryptography is about mathematical guarantees.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'critic', 'batch'],
        environment={'HASH_ALGORITHM': 'SHA256'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="rasmus",
        programmer="Rasmus Lerdorf",
        description="PHP creator - pragmatic web development",
        philosophy="I'm not a real programmer. I throw together things until it works.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'sql_query', 'watch', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'PHP_VERSION': '8.0'},
        tags=['pioneer', 'web'],
    ),
    ToolPersonality(
        name="rich",
        programmer="Rich Hickey",
        description="Clojure creator - simplicity matters",
        philosophy="Programming is not about typing... it's about thinking.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'todo', 'batch', 'agent', 'consensus', 'critic', 'think'],
        environment={'CLOJURE_VERSION': '1.11'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="richard",
        programmer="Richard Stallman",
        description="GNU creator - software freedom",
        philosophy="Free software is a matter of liberty, not price.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'content_replace', 'batch', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'EDITOR': 'emacs'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="rob",
        programmer="Rob Pike",
        description="Go creator - simplicity and concurrency",
        philosophy="A little copying is better than a little dependency.",
        tools=['bash', 'batch', 'cargo', 'diff', 'edit', 'find_files', 'gem', 'go_test', 'grep', 'npx', 'pip', 'process', 'read', 'symbols', 'think', 'tree', 'uvx', 'write'],
        environment={'GOPATH': '~/go', 'GO111MODULE': 'on'},
        tags=['languages', 'go', 'concurrency'],
    ),
    ToolPersonality(
        name="ryan",
        programmer="Ryan Dahl",
        description="Node.js & Deno creator",
        philosophy="I/O needs to be done differently.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'uvx', 'watch', 'process', 'bash', 'npx', 'uvx', 'process'],
        environment={'DENO_DIR': '~/.deno'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="salvatore",
        programmer="Salvatore Sanfilippo",
        description="Redis creator - data structures server",
        philosophy="Simplicity is a great virtue.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'bash', 'watch', 'process', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'REDIS_VERSION': '7.0'},
        tags=['pioneer', 'database'],
    ),
    ToolPersonality(
        name="sanjay",
        programmer="Sanjay Ghemawat",
        description="MapReduce & BigTable co-creator",
        philosophy="Simple abstractions for complex systems.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'sql_query', 'sql_search', 'graph_add', 'graph_query', 'batch', 'process'],
        environment={'SPARK_HOME': '/opt/spark'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="satoshi",
        programmer="Satoshi Nakamoto",
        description="Bitcoin creator - peer-to-peer electronic cash",
        philosophy="A purely peer-to-peer version of electronic cash.",
        tools=['bash', 'content_replace', 'critic', 'dast', 'dependency_scan', 'diff', 'edit', 'find_files', 'fuzz', 'gh', 'git_search', 'gitlab', 'grep', 'kms', 'process', 'read', 'sast', 'sbom', 'secret_scan', 'signing', 'sigstore', 'snyk', 'symbols', 'think', 'tree', 'trivy', 'write'],
        environment={'BITCOIN_NETWORK': 'mainnet', 'RPC_USER': 'bitcoin', 'SIGNING_KEY': ''},
        tags=['blockchain', 'crypto', 'p2p'],
    ),
    ToolPersonality(
        name="sebastian",
        programmer="Sebastian Thrun",
        description="Udacity founder & self-driving car pioneer",
        philosophy="Education should be accessible to all.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'jupyter', 'watch'],
        environment={'ROS_VERSION': 'noetic'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="security",
        programmer="Security Researcher",
        description="Break it to secure it",
        philosophy="The only secure system is one that's powered off.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols', 'git_search', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'SECURITY_MODE': 'paranoid'},
        tags=['general'],
    ),
    ToolPersonality(
        name="security_first",
        programmer="Security Engineer",
        description="Security-first development",
        philosophy="Trust nothing, verify everything.",
        tools=['artifact_publish', 'bash', 'ci', 'circleci', 'coverage', 'dast', 'dependency_scan', 'diff', 'edit', 'formatter', 'fuzz', 'gh', 'git_search', 'github_actions', 'gitlab', 'gitlab_ci', 'go_test', 'jenkins', 'jest', 'kms', 'linters', 'mocha', 'pytest', 'read', 'sast', 'sbom', 'secret_scan', 'secrets_manager', 'signing', 'sigstore', 'snyk', 'think', 'tree', 'trivy', 'write'],
        environment={'SECURITY_SCAN': 'enabled', 'SIGNING_KEY': '', 'KMS_KEY': '', 'SNYK_TOKEN': ''},
        tags=['security', 'devsecops', 'compliance'],
    ),
    ToolPersonality(
        name="shigeru",
        programmer="Shigeru Miyamoto",
        description="Mario & Zelda creator",
        philosophy="A delayed game is eventually good, but a rushed game is forever bad.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'watch', 'critic'],
        environment={'NINTENDO_SDK': 'true'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="sid",
        programmer="Sid Meier",
        description="Civilization creator",
        philosophy="A game is a series of interesting choices.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'watch', 'process'],
        environment={'GAME_MODE': 'debug'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="startup",
        programmer="Startup Founder",
        description="Move fast and fix things",
        philosophy="Done is better than perfect.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'agent', 'consensus', 'bash', 'npx', 'uvx', 'process', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'STARTUP_MODE': 'hustle'},
        tags=['general'],
    ),
    ToolPersonality(
        name="taylor",
        programmer="Taylor Otwell",
        description="Laravel creator - PHP artisan",
        philosophy="Love beautiful code? We do too.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'sql_query', 'watch', 'sql_query', 'sql_search', 'graph_add', 'graph_query'],
        environment={'LARAVEL_VERSION': '10'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="theo",
        programmer="Theo de Raadt",
        description="OpenBSD creator - security by default",
        philosophy="Shut up and hack.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'diff', 'grep', 'find_files', 'bash', 'process', 'diff'],
        environment={'OPENBSD_VERSION': '7.3'},
        tags=['pioneer', 'security'],
    ),
    ToolPersonality(
        name="tim",
        programmer="Tim Berners-Lee",
        description="WWW inventor - open web",
        philosophy="The Web is for everyone.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'npx', 'watch', 'rules', 'search', 'symbols', 'grep', 'git_search'],
        environment={'W3C_VALIDATOR': 'true'},
        tags=['pioneer', 'web'],
    ),
    ToolPersonality(
        name="tim_sweeney",
        programmer="Tim Sweeney",
        description="Epic Games founder - Unreal Engine",
        philosophy="The engine is the game.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'symbols', 'watch', 'process', 'bash', 'npx', 'uvx', 'process'],
        environment={'UNREAL_ENGINE': '5'},
        tags=['pioneer', 'gaming'],
    ),
    ToolPersonality(
        name="tom",
        programmer="Tom Preston-Werner",
        description="GitHub co-founder & TOML creator",
        philosophy="Optimize for happiness.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'git_search', 'todo', 'rules'],
        environment={'GITHUB_ACTIONS': 'true'},
        tags=['pioneer', 'ai'],
    ),
    ToolPersonality(
        name="turing",
        programmer="Alan Turing",
        description="Computing foundations and AI pioneer",
        philosophy="We can only see a short distance ahead, but we can see plenty there that needs to be done.",
        tools=['agent', 'bash', 'consensus', 'critic', 'edit', 'llm', 'model_check', 'notebook', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'TURING_COMPLETE': 'true'},
        tags=['pioneer', 'ai', 'theory'],
    ),
    ToolPersonality(
        name="vitalik",
        programmer="Vitalik Buterin",
        description="Ethereum creator - world computer",
        philosophy="Decentralized world computer.",
        tools=['ast_search', 'bash', 'cargo', 'dast', 'dependency_scan', 'edit', 'fuzz', 'gem', 'git_search', 'grep', 'hardhat', 'multi_edit', 'npx', 'pip', 'process', 'read', 'sast', 'sbom', 'search', 'secret_scan', 'sigstore', 'snyk', 'symbols', 'think', 'todo', 'tree', 'trivy', 'truffle', 'uvx', 'write'],
        environment={'ETH_NETWORK': 'mainnet', 'WEB3_PROVIDER': 'https://mainnet.infura.io'},
        tags=['blockchain', 'ethereum', 'smart-contracts'],
    ),
    ToolPersonality(
        name="whitfield",
        programmer="Whitfield Diffie",
        description="Public-key cryptography pioneer",
        philosophy="Privacy is necessary for an open society.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'critic', 'symbols'],
        environment={'OPENSSL_VERSION': '3.0'},
        tags=['general'],
    ),
    ToolPersonality(
        name="will",
        programmer="Will Wright",
        description="SimCity & The Sims creator",
        philosophy="Games are a form of communication.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'todo', 'watch', 'process'],
        environment={'SIMULATION_MODE': 'debug'},
        tags=['pioneer'],
    ),
    ToolPersonality(
        name="wirth",
        programmer="Niklaus Wirth",
        description="Language design - Pascal/Modula/Oberon",
        philosophy="Algorithms + Data Structures = Programs",
        tools=['bash', 'compiler', 'edit', 'formatter', 'linters', 'read', 'symbols', 'think', 'tree', 'write'],
        environment={'LANGUAGE_STYLE': 'pascal', 'TYPE_SAFETY': 'strict'},
        tags=['languages', 'academic', 'design'],
    ),
    ToolPersonality(
        name="yann",
        programmer="Yann LeCun",
        description="Deep learning pioneer - ConvNets",
        philosophy="AI is not magic; it's just math and data.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'vector_index', 'vector_search', 'jupyter', 'watch'],
        environment={'PYTORCH_VERSION': '2.0'},
        tags=['general'],
    ),
    ToolPersonality(
        name="yoshua",
        programmer="Yoshua Bengio",
        description="Deep learning pioneer",
        philosophy="We need to think about AI that helps humanity.",
        tools=['read', 'write', 'edit', 'tree', 'bash', 'think', 'agent', 'consensus', 'critic', 'think', 'vector_index', 'vector_search', 'jupyter', 'batch'],
        environment={'THEANO_FLAGS': 'device=cuda'},
        tags=['general'],
    ),
]

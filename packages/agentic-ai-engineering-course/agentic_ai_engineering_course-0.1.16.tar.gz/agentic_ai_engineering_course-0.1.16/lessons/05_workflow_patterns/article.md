# LLM Workflow Patterns
### From monolithic to modular LLM systems

## Stop Trying to Solve Everything with a Single Prompt

A common trap in AI engineering is treating Large Language Models (LLMs) as magical black boxes. The thinking goes: if you just craft a sufficiently complex, elaborate prompt, the LLM can solve any multi-step problem in one shot. This approach is a recipe for building brittle, unreliable systems that are impossible to debug and unfit for production. When the model inevitably fails, you have no idea which of the 20 instructions in your mega-prompt was the weak link.

This is not real engineering.

The truth is, building robust and reliable LLM applications requires modularity. Instead of one giant, monolithic prompt, we should break down complex problems into smaller, manageable steps. This lesson is about the fundamental patterns that enable this modular approach: chaining, parallelization, and routing. These are the essential building blocks for moving from simple prompts to sophisticated, production-grade workflows. We will explore how to implement these patterns to build powerful, predictable, and maintainable AI systems.

## The Challenge with Complex Single LLM Calls

Attempting to solve a complex, multi-step task with a single, large LLM call is an anti-pattern. While it might seem efficient, it introduces a host of engineering problems that make the system fragile and difficult to maintain. The core issue is a lack of control and observability. When you bundle numerous instructions into one prompt, you lose the ability to isolate and debug failures. If the final output is wrong, you have no way of knowing if the model misunderstood an early instruction or simply ignored a crucial part of your request. This leads to inconsistent and unpredictable outputs, undermining reliability for structured tasks, as unconstrained prompting can lead to output label inconsistency and schema drift [[1]](https://arxiv.org/pdf/2309.08181).

This approach also suffers from the "lost in the middle" problem, where models tend to pay less attention to information located in the middle of a long context window [[2]](https://arxiv.org/html/2410.23884v1). The model might perform well on the first and last instructions but forget or misinterpret the ones in between, especially in long narratives with many events [[2]](https://arxiv.org/html/2410.23884v1). Furthermore, single prompts can be highly sensitive to minor input changes, where small phrasing differences can cause dramatically different outputs, harming reproducibility [[3]](https://www.getambassador.io/blog/prompt-engineering-for-llms). Stuffing too many instructions into a single prompt can also lead to overstuffed context windows, potentially truncating inputs and causing incomplete outputs [[3]](https://www.getambassador.io/blog/prompt-engineering-for-llms).

Let's make this concrete with an example. Imagine we want to generate a Frequently Asked Questions (FAQ) page from a few documents about renewable energy. A naive approach would be to stuff all the content and instructions into a single prompt.

1.  First, we set up our environment. We use the Google Gemini library to initialize the client and define our model ID.

    ```python
    import asyncio
    from enum import Enum
    import random
    import time

    from pydantic import BaseModel, Field
    from google import genai
    from google.genai import types

    # Initialize the Gemini Client
    client = genai.Client()

    # Define Constants
    MODEL_ID = "gemini-2.5-flash"
    ```

2.  Next, we define our source content, which consists of three mock web pages about renewable energy. We combine their titles and content into a single string for the LLM to process.

    ```python
    webpage_1 = {
        "title": "The Benefits of Solar Energy",
        "content": """
        Solar energy is a renewable powerhouse...
        """,
    }

    webpage_2 = {
        "title": "Understanding Wind Turbines",
        "content": """
        Wind turbines are towering structures...
        """,
    }

    webpage_3 = {
        "title": "Energy Storage Solutions",
        "content": """
        Effective energy storage is the key...
        """,
    }

    all_sources = [webpage_1, webpage_2, webpage_3]

    # We'll combine the content for the LLM to process
    combined_content = "\n\n".join(
        [f"Source Title: {source['title']}\nContent: {source['content']}" for source in all_sources]
    )
    ```

3.  Now, we create a single, complex prompt that asks the LLM to generate 10 FAQs, provide answers, and cite the sources—all at once. We use Pydantic models to enforce a structured JSON output, a concept we covered in a previous lesson on structured outputs.

    ```python
    # Pydantic classes for structured outputs
    class FAQ(BaseModel):
        """A FAQ is a question and answer pair, with a list of sources used to answer the question."""
        question: str = Field(description="The question to be answered")
        answer: str = Field(description="The answer to the question")
        sources: list[str] = Field(description="The sources used to answer the question")

    class FAQList(BaseModel):
        """A list of FAQs"""
        faqs: list[FAQ] = Field(description="A list of FAQs")

    # This prompt tries to do everything at once
    n_questions = 10
    prompt_complex = f"""
    Based on the provided content from three webpages, generate a list of exactly {n_questions} frequently asked questions (FAQs).
    For each question, provide a concise answer derived ONLY from the text.
    After each answer, you MUST include a list of the 'Source Title's that were used to formulate that answer.

    <provided_content>
    {combined_content}
    </provided_content>
    """.strip()

    # Generate FAQs
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FAQList
    )
    response_complex = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_complex,
        config=config
    )
    result_complex = response_complex.parsed
    ```

Here is a sample of the output:
```json
{
  "question": "Why is energy storage crucial for renewable energy sources like solar and wind?",
  "answer": "Effective energy storage is key to unlocking the full potential of renewable sources because it allows storing excess energy when plentiful and releasing it when needed, which is crucial for a stable power grid.",
  "sources": [
    "Energy Storage Solutions"
  ]
}
```

At first glance, the output might seem acceptable. However, with complex instructions, subtle inaccuracies creep in. In the example above, the answer is derived from both "Energy Storage Solutions" and "Understanding Wind Turbines," but the model only cited one source. The more complex the task, the more such errors will occur. This single-prompt approach is fundamentally brittle and not suitable for building systems that require high accuracy and reliability.

## The Power of Modularity: Why Chain LLM Calls?

The solution to the fragility of single, complex prompts is prompt chaining. This is a simple yet powerful "divide-and-conquer" strategy for LLM workflows. Instead of asking the model to do everything at once, we break down the task into a sequence of smaller, more focused sub-tasks. The output of one LLM call then becomes the input for the next, creating a chain of operations that guides the model toward the final, desired result [[4]](https://dev.to/kapusto/enhancing-large-language-model-performance-with-prompt-chaining-2p84).

This modular approach brings significant engineering benefits. First, it dramatically improves accuracy and reliability. A simple, targeted prompt is much easier for an LLM to understand and execute correctly than a long, convoluted one. Each step in the chain has a single, clear objective, which minimizes the chances of misinterpretation or hallucination [[5]](https://www.vellum.ai/blog/what-is-prompt-chaining). By segmenting the interaction into distinct steps, each prompt becomes a module with explicit inputs and outputs, supporting structured workflows and clearer boundaries between tasks [[4]](https://dev.to/kapusto/enhancing-large-language-model-performance-with-prompt-chaining-2p84).

Second, modularity makes the system far easier to debug and maintain. When a workflow is broken into discrete steps, you can inspect the input and output of each one. If a failure occurs, you can quickly pinpoint the exact step in the chain that caused the problem, rather than trying to decipher a single, failed mega-prompt [[6]](https://blog.promptlayer.com/what-is-prompt-chaining/). This step-by-step output increases explainability and makes it easier to trace how conclusions are reached, which is crucial for building and operating production systems [[7]](https://www.voiceflow.com/blog/prompt-chaining).

Finally, chaining offers flexibility. You can optimize each step independently. For instance, you could use a fast, cheaper model like Haiku for a simple classification task and a more powerful, expensive model like Opus for a complex reasoning step. This allows you to balance cost, latency, and quality across the workflow [[5]](https://www.vellum.ai/blog/what-is-prompt-chaining).

However, this approach is not without trade-offs. Chaining multiple LLM calls will inevitably increase latency and cost compared to a single call [[8]](https://aisdr.com/blog/what-is-prompt-chaining/), [[9]](https://blog.promptlayer.com/what-is-prompt-chaining/). Each additional call adds to the total processing time and token count, which can lead to significantly higher API bills, especially as the number of steps or the volume of requests increases [[10]](https://ai.plainenglish.io/prompt-chaining-is-dead-long-live-prompt-stuffing-58a1c08820c5). There is also a risk of information loss between steps; if an intermediate step produces a poor-quality summary, that error will cascade down the chain and impact the final output. Critically, some instructions lose their intended meaning when separated—a task that is clear in a single prompt can become ambiguous when broken apart, leading to subtle but significant errors in the final result. Furthermore, managing multiple interconnected prompts adds design and maintenance burden, often requiring additional "glue code" to connect the different pieces, which increases engineering complexity [[9]](https://blog.promptlayer.com/what-is-prompt-chaining/), [[10]](https://ai.plainenglish.io/prompt-chaining-is-dead-long-live-prompt-stuffing-58a1c08820c5), [[11]](https://www.humanfirst.ai/blog/prompt-chaining). As engineers, we must weigh these trade-offs and design our workflows to be as efficient and robust as possible.

## Building a Sequential Workflow: FAQ Generation Pipeline

Let's put the theory of prompt chaining into practice by refactoring our FAQ generation example. Instead of relying on one giant, monolithic prompt, we will build a 3-step sequential pipeline. This approach breaks down the complex task into smaller, more manageable units, making the entire process more robust and transparent.

Here are the three distinct steps in our sequential pipeline:

1.  **Generate Questions**: The initial step involves an LLM call to read the source content and generate a list of relevant questions. This focuses the LLM solely on question formulation.
2.  **Answer Questions**: For each generated question, a second LLM call will produce a concise answer based on the provided source content. This step ensures answers are directly grounded in the given text.
3.  **Find Sources**: For each question-and-answer pair, a third LLM call will identify the original source titles used. This crucial step adds traceability and verifiability to our generated FAQs.

This modular approach ensures that each step has a single responsibility, leading to more consistent and traceable results. By isolating concerns, we can better control the output of each stage and pinpoint issues if they arise.

First, we create a function to generate the initial list of questions. This function takes the combined content and the desired number of questions as input. Its sole purpose is to extract potential questions from the provided text. We use a Pydantic model, `QuestionList`, to ensure the output is a structured list of strings, a concept we explored in Lesson 4 on structured outputs. This structured output is vital for the next steps in our chain.
```python
class QuestionList(BaseModel):
    """A list of questions"""
    questions: list[str] = Field(description="A list of questions")

prompt_generate_questions = """
Based on the content below, generate a list of {n_questions} relevant and distinct questions that a user might have.

<provided_content>
{combined_content}
</provided_content>
""".strip()

def generate_questions(content: str, n_questions: int = 10) -> list[str]:
    """
    Generate a list of questions based on the provided content.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=QuestionList
    )
    response_questions = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_generate_questions.format(n_questions=n_questions, combined_content=content),
        config=config
    )

    return response_questions.parsed.questions
```

Next, we define a function to answer a given question. This prompt is tightly focused: it instructs the model to use *only* the provided content to formulate a concise answer. This strict constraint is essential for preventing the LLM from hallucinating information, ensuring that every answer is directly supported by the source material.
```python
prompt_answer_question = """
Using ONLY the provided content below, answer the following question.
The answer should be concise and directly address the question.

<question>
{question}
</question>

<provided_content>
{combined_content}
</provided_content>
""".strip()

def answer_question(question: str, content: str) -> str:
    """
    Generate an answer for a specific question using only the provided content.
    """
    answer_response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_answer_question.format(question=question, combined_content=content),
    )
    return answer_response.text
```

Finally, we create a function to find the sources for a given question-and-answer pair. This step adds the traceability that was missing from our single-prompt approach. By dedicating a specific step to source identification, we can ensure that each answer is accurately attributed, which is critical for building trustworthy AI applications. This function also uses a Pydantic model, `SourceList`, to return a structured list of source titles.
```python
class SourceList(BaseModel):
    """A list of source titles that were used to answer the question"""
    sources: list[str] = Field(description="A list of source titles that were used to answer the question")

prompt_find_sources = """
You will be given a question and an answer that was generated from a set of documents.
Your task is to identify which of the original documents were used to create the answer.

<question>
{question}
</question>

<answer>
{answer}
</answer>

<provided_content>
{combined_content}
</provided_content>
""".strip()

def find_sources(question: str, answer: str, content: str) -> list[str]:
    """
    Identify which sources were used to generate an answer.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=SourceList
    )
    sources_response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt_find_sources.format(question=question, answer=answer, combined_content=content),
        config=config
    )
    return sources_response.parsed.sources
```

Now, we can combine these functions into a sequential workflow. The `sequential_workflow` function orchestrates the entire process, calling each of the three steps in order for every question. This structured execution ensures that the data flows logically from one specialized task to the next.
```mermaid
graph TD
    A[Input Content] --> B{Step 1: Generate Questions};
    B --> C{Step 2: Answer Questions};
    C --> D{Step 3: Find Sources};
    D --> E[Formatted FAQ];
```
Figure 1: A diagram illustrating the sequential FAQ generation pipeline.
```python
def sequential_workflow(content, n_questions=10) -> list[FAQ]:
    """
    Execute the complete sequential workflow for FAQ generation.
    """
    # Generate questions
    questions = generate_questions(content, n_questions)

    # Answer and find sources for each question sequentially
    final_faqs = []
    for question in questions:
        # Generate an answer for the current question
        answer = answer_question(question, content)

        # Identify the sources for the generated answer
        sources = find_sources(question, answer, content)

        faq = FAQ(
            question=question,
            answer=answer,
            sources=sources
        )
        final_faqs.append(faq)

    return final_faqs

# Execute the sequential workflow (measure time for comparison)
start_time = time.monotonic()
sequential_faqs = sequential_workflow(combined_content, n_questions=4)
end_time = time.monotonic()
print(f"Sequential processing completed in {end_time - start_time:.2f} seconds")
```

Running this code produces the following output:
```text
Sequential processing completed in 22.20 seconds
```

The final result is a list of well-formed FAQs, each with a question, a focused answer, and accurate source citations. This chained approach took longer to execute, but it gives us a more reliable, debuggable, and maintainable system. While the increased latency is a trade-off, the benefits of improved accuracy and control often outweigh this disadvantage for production-grade AI applications.

## Optimizing Sequential Workflows With Parallel Processing

The sequential workflow we built is robust, but it's slow. Each LLM call is blocking, meaning the workflow must wait for one step to complete before the next one can begin. For our FAQ example, processing just four questions results in nine separate, sequential API calls—one to generate the questions, and then two for each question (answer and sources). This cumulative latency can become a major bottleneck.

We can optimize this process by introducing parallel processing. Since the tasks of answering and finding sources for each question are independent of each other, we can execute them concurrently. This approach can dramatically reduce the total execution time.

To implement this, we will use Python's `asyncio` library to create asynchronous versions of our `answer_question` and `find_sources` functions.

1.  We define `answer_question_async` and `find_sources_async` to allow non-blocking API calls.

    ```python
    async def answer_question_async(question: str, content: str) -> str:
        """
        Async version of answer_question function.
        """
        prompt = prompt_answer_question.format(question=question, combined_content=content)
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text

    async def find_sources_async(question: str, answer: str, content: str) -> list[str]:
        """
        Async version of find_sources function.
        """
        prompt = prompt_find_sources.format(question=question, answer=answer, combined_content=content)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SourceList
        )
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        return response.parsed.sources
    ```

2.  Next, we create a new asynchronous function, `process_question_parallel`, which handles a single question by calling both the `answer_question_async` and `find_sources_async` functions.

    ```python
    async def process_question_parallel(question: str, content: str) -> FAQ:
        """
        Process a single question by generating answer and finding sources in parallel.
        """
        answer = await answer_question_async(question, content)
        sources = await find_sources_async(question, answer, content)
        return FAQ(
            question=question,
            answer=answer,
            sources=sources
        )
    ```

3.  Finally, we create the `parallel_workflow`. This function first generates the list of questions synchronously. Then, it uses `asyncio.gather` to execute the `process_question_parallel` function for all questions concurrently.

    ```python
    async def parallel_workflow(content: str, n_questions: int = 10) -> list[FAQ]:
        """
        Execute the complete parallel workflow for FAQ generation.
        """
        # Generate questions (this step remains synchronous)
        questions = generate_questions(content, n_questions)

        # Process all questions in parallel
        tasks = [process_question_parallel(question, content) for question in questions]
        parallel_faqs = await asyncio.gather(*tasks)

        return parallel_faqs

    # Execute the parallel workflow (measure time for comparison)
    start_time = time.monotonic()
    parallel_faqs = await parallel_workflow(combined_content, n_questions=4)
    end_time = time.monotonic()
    print(f"Parallel processing completed in {end_time - start_time:.2f} seconds")
    ```

When we run this parallel workflow, the output shows a significant improvement in performance:
```text
Parallel processing completed in 8.98 seconds
```

By running the independent tasks in parallel, we cut the execution time by more than half. This demonstrates how parallel processing can dramatically reduce latency for tasks where sub-components are independent. However, this optimization comes with its own set of trade-offs. While sequential processing is easier to debug, parallel processing introduces more complexity in managing state and handling errors.

⚠️ A critical real-world consideration when implementing parallel LLM calls is API rate limiting. LLM providers enforce quotas, typically measured in requests-per-minute (RPM) or tokens-per-minute (TPM). Making many parallel calls can easily exceed these limits, leading to `429` errors, which indicate "Too Many Requests" [[12]](https://platform.openai.com/docs/guides/rate-limits), [[13]](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas). Production systems must implement robust error handling strategies to manage this. This includes using exponential backoff with jitter, where your system retries failed requests after increasing delays, and respecting any `Retry-After` headers provided by the API [[12]](https://platform.openai.com/docs/guides/rate-limits), [[14]](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits). Additionally, implementing client-side queueing or dynamically adjusting concurrency based on real-time rate limit headers can help manage throughput and stay within API limits [[12]](https://platform.openai.com/docs/guides/rate-limits), [[13]](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas), [[15]](https://docs.anthropic.com/en/docs/build-with-claude/rate-limits).

## Introducing Dynamic Behavior: Routing and Conditional Logic

So far, our workflows have followed a fixed, linear path. While this works for straightforward tasks, real-world applications often need to adapt dynamically based on user input. A customer service bot, for example, cannot use the same script for a billing question as it would for a technical support issue. Each query type demands a distinct approach.

This is where routing comes in. Routing introduces conditional logic into your workflows, allowing them to adapt intelligently. Instead of following a single, fixed path, your workflow can branch dynamically based on the input's characteristics.

The core idea is to use an LLM call as a classification step. This LLM acts as a dispatcher, interpreting the input's intent and determining which specific branch of the workflow to execute [[16]](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-routing.html). This enables the system to triage requests and direct them to the most appropriate specialized handler. This approach aligns perfectly with the "divide-and-conquer" principle. By routing different input types to specialized handlers, you keep each prompt simple and focused, adhering to the principle of single responsibility. This separation of concerns is crucial, as trying to optimize a single prompt for multiple input types can degrade performance on others [[17]](https://arize.com/docs/phoenix/learn), [[18]](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns). This modularity makes the overall system more robust, maintainable, and easier to optimize [[19]](https://mikulskibartosz.name/ai-workflow-design-patterns).

## Building a Basic Routing Workflow

We will now apply the theory of routing to a practical example: a simple customer service workflow. This system first classifies the user's intent, then routes the query to a specialized handler. A robust routing workflow requires careful design of the classification step to accurately interpret user queries.

Our workflow supports three intents: `Technical Support`, `Billing Inquiry`, and `General Question`. We begin by defining an `Enum` and a Pydantic model to structure our classification step. This ensures the output is predictable and easy to use, a concept we explored in Lesson 4.
```python
class IntentEnum(str, Enum):
    """
    Defines the allowed values for the 'intent' field.
    """
    TECHNICAL_SUPPORT = "Technical Support"
    BILLING_INQUIRY = "Billing Inquiry"
    GENERAL_QUESTION = "General Question"

class UserIntent(BaseModel):
    """
    Defines the expected response schema for the intent classification.
    """
    intent: IntentEnum = Field(description="The intent of the user's query")
```

Next, we create the `classify_intent` function. This function uses an LLM to categorize the user's query into one of our predefined intents. The prompt guides the LLM to select from the specified categories, ensuring a focused classification.
```python
prompt_classification = """
Classify the user's query into one of the following categories.

<categories>
{categories}
</categories>

<user_query>
{user_query}
</user_query>
""".strip()

def classify_intent(user_query: str) -> IntentEnum:
    """Uses an LLM to classify a user query."""
    prompt = prompt_classification.format(
        user_query=user_query,
        categories=[intent.value for intent in IntentEnum]
    )
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=UserIntent
    )
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=config
    )
    return response.parsed.intent
```

When designing the prompt for intent classification, it's best practice to define a clear, precise, and comprehensive taxonomy of intents to guide the LLM's classification process [[20]](https://arxiv.org/html/2402.02136v2). Providing high-quality, representative examples for each intent is also critical for accuracy, especially for edge cases [[21]](https://rasa.com/docs/rasa/next/llms/llm-intent/), [[22]](https://spotintelligence.com/2023/11/03/intent-classification-nlp/). Some systems even use a two-stage architecture where an initial model retrieves top candidate intents, and then an LLM selects the best match from that narrowed set to improve precision [[23]](https://www.voiceflow.com/pathways/5-tips-to-optimize-your-llm-intent-classification-prompts).

Now, we define specialized prompts for each intent. Each prompt provides a specific persona and instructions for the LLM to follow. This ensures the response is tailored to the classified intent.
```python
prompt_technical_support = """
You are a helpful technical support agent.

Here's the user's query:
<user_query>
{user_query}
</user_query>

Provide a helpful first response, asking for more details like what troubleshooting steps they have already tried.
""".strip()

prompt_billing_inquiry = """
You are a helpful billing support agent.

Here's the user's query:
<user_query>
{user_query}
</user_query>

Acknowledge their concern and inform them that you will need to look up their account, asking for their account number.
""".strip()

prompt_general_question = """
You are a general assistant.

Here's the user's query:
<user_query>
{user_query}
</user_query>

Apologize that you are not sure how to help.
""".strip()
```

Finally, we create the `handle_query` function, which acts as our router. It takes the user's query and the classified intent, then selects the appropriate prompt to generate a response. This conditional logic allows the workflow to dynamically adapt.
```mermaid
graph TD
    A[User Query] --> B{Classify Intent};
    B -- Technical Support --> C[Technical Handler];
    B -- Billing Inquiry --> D[Billing Handler];
    B -- General Question --> E[General Handler];
    C --> F[Generated Response];
    D --> F;
    E --> F;
```
Figure 2: A diagram illustrating the routing workflow with conditional branching.
```python
def handle_query(user_query: str, intent: str) -> str:
    """Routes a query to the correct handler based on its classified intent."""
    if intent == IntentEnum.TECHNICAL_SUPPORT:
        prompt = prompt_technical_support.format(user_query=user_query)
    elif intent == IntentEnum.BILLING_INQUIRY:
        prompt = prompt_billing_inquiry.format(user_query=user_query)
    else:
        prompt = prompt_general_question.format(user_query=user_query)
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    return response.text
```

When we run a query like `"I think there is a mistake on my last invoice."`, the `classify_intent` function correctly identifies it as a `BILLING_INQUIRY`. The `handle_query` function then routes it to the billing handler, which generates a tailored response:
```text
I'm sorry to hear you think there might be a mistake on my last invoice. I can definitely help you look into that!

To access your account and investigate the charges, could you please provide your account number?
```

This routing pattern allows us to build more sophisticated applications by composing simple, specialized components. It also enables us to implement robust fallback and failover strategies, ensuring that even unclassified queries are handled gracefully [[24]](https://www.requesty.ai/blog/intelligent-llm-routing-in-enterprise-ai-uptime-cost-efficiency-and-model).

## Orchestrator-Worker Pattern: Dynamic Task Decomposition

The orchestrator-worker pattern offers a flexible approach for handling complex tasks where you cannot know the necessary steps in advance. In this pattern, a central "orchestrator" LLM analyzes a complex query, dynamically breaks it down into smaller sub-tasks, and delegates them to specialized "worker" LLMs. The orchestrator then combines the results from these workers into a single, cohesive response [[25]](https://www.anthropic.com/research/building-effective-agents).

This pattern's core strength lies in its dynamic nature. Unlike a predefined parallel workflow where sub-tasks are fixed, the orchestrator determines them on the fly based on the specific input. This allows it to adapt the number, type, and sequencing of subtasks at runtime, making it ideal for complex scenarios like a customer support ticket that touches on multiple issues—billing, returns, and order status—all at once [[25]](https://www.anthropic.com/research/building-effective-agents), [[26]](https://huggingface.co/blog/dcarpintero/design-patterns-for-building-agentic-workflows).

While powerful, this pattern introduces its own implementation challenges. The central orchestrator can become a bottleneck if its planning and monitoring responsibilities are serialized [[27]](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-orchestration.html), [[28]](https://www.anthropic.com/research/building-effective-agents). You also face the risk of incomplete decomposition, where the orchestrator might miss necessary subtasks, or conflicting worker outputs that are difficult to reconcile during synthesis [[28]](https://www.anthropic.com/research/building-effective-agents). Ensuring clear boundaries and consistent prompt schemas between the orchestrator and workers is crucial to avoid misrouted subtasks and synthesis errors [[29]](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns). The synthesizer's role in combining outputs is critical, but it faces challenges in resolving conflicts between specialized outputs and normalizing formats to ensure the final product is cohesive [[30]](https://javaaidev.com/docs/agentic-patterns/patterns/orchestrator-workers-workflow/), [[31]](https://bootcamptoprod.com/spring-ai-orchestrator-workers-workflow-guide/).

Let's build an example. Our orchestrator will take a complex customer query and break it down into a list of structured tasks.

1.  **Define the data structures for tasks**: We start by defining the `QueryTypeEnum` to categorize different types of queries, along with `Task` and `TaskList` Pydantic models. This structures the orchestrator's output.

    ```python
    class QueryTypeEnum(str, Enum):
        BILLING_INQUIRY = "BillingInquiry"
        PRODUCT_RETURN = "ProductReturn"
        STATUS_UPDATE = "StatusUpdate"

    class Task(BaseModel):
        query_type: QueryTypeEnum
        invoice_number: str | None = None
        product_name: str | None = None
        reason_for_return: str | None = None
        order_id: str | None = None

    class TaskList(BaseModel):
        tasks: list[Task]
    ```

2.  **Implement the orchestrator function**: This function takes a complex user query and crafts a prompt to guide the LLM in breaking it down into structured sub-tasks.

    ```python
    prompt_orchestrator = f"""
    You are a master orchestrator. Your job is to break down a complex user query into a list of sub-tasks.
    Each sub-task must have a "query_type" and its necessary parameters.

    The possible "query_type" values and their required parameters are:
    1. "{QueryTypeEnum.BILLING_INQUIRY.value}": Requires "invoice_number".
    2. "{QueryTypeEnum.PRODUCT_RETURN.value}": Requires "product_name" and "reason_for_return".
    3. "{QueryTypeEnum.STATUS_UPDATE.value}": Requires "order_id".

    Here's the user's query.

    <user_query>
    {{query}}
    </user_query>
    """.strip()

    def orchestrator(query: str) -> list[Task]:
        """Breaks down a complex query into a list of tasks."""
        prompt = prompt_orchestrator.format(query=query)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TaskList
        )
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=config
        )
        return response.parsed.tasks
    ```

Next, we define specialized worker functions for each task type. For example, the `handle_billing_worker` simulates opening an investigation, the `handle_return_worker` generates a Return Merchandise Authorization (RMA) number, and the `handle_status_worker` fetches order details.
```python
def handle_billing_worker(invoice_number: str, original_user_query: str) -> BillingTask:
    """Handles a billing inquiry."""
    # ... logic to extract concern and simulate investigation ...
    return task

def handle_return_worker(product_name: str, reason_for_return: str) -> ReturnTask:
    """Handles a product return request."""
    # ... logic to generate RMA and shipping instructions ...
    return task

def handle_status_worker(order_id: str) -> StatusTask:
    """Handles an order status update request."""
    # ... logic to fetch order status ...
    return task
```

After the workers complete their tasks, a final `synthesizer` LLM combines their structured outputs into a single, user-friendly message. This step is crucial for presenting a cohesive response to the user.
```mermaid
graph TD
    A[Complex User Query] --> B{Orchestrator LLM};
    B -- Decomposes into Sub-Tasks --> C[Task 1: Billing];
    B -- Decomposes into Sub-Tasks --> D[Task 2: Return];
    B -- Decomposes into Sub-Tasks --> E[Task 3: Status];
    C --> F[Billing Worker];
    D --> G[Return Worker];
    E --> H[Status Worker];
    F --> I{Synthesizer LLM};
    G --> I;
    H --> I;
    I --> J[Cohesive Response];
```
Figure 3: A flowchart illustrating the orchestrator-worker pattern.

The main pipeline function coordinates this entire flow.
```python
def process_user_query(user_query):
    """Processes a query using the Orchestrator-Worker-Synthesizer pattern."""
    # 1. Run orchestrator
    tasks_list = orchestrator(user_query)

    # 2. Run workers in parallel
    worker_results = []
    # ... dispatch tasks to appropriate workers ...

    # 3. Run synthesizer
    final_user_message = synthesizer(worker_results)
    print(final_user_message)
```

When you feed it a complex query like, `"Hi, I have a question about invoice #INV-7890. Also, I'd like to return the 'SuperWidget 5000'. Finally, can you update me on order #A-12345?"`, the orchestrator correctly identifies the three distinct sub-tasks. The workers process them, and the synthesizer produces a single, organized response covering all points. This dynamic decomposition allows you to handle highly variable and complex inputs in a structured and scalable way.

## Conclusion: From Simple Chains to Sophisticated AI Systems

We have moved from the naive approach of using a single, complex LLM call to a more robust, modular way of building workflows. By embracing patterns like chaining, parallelization, routing, and the orchestrator-worker model, we can construct AI applications that are more reliable, debuggable, and scalable. These are not just abstract concepts; they are the practical engineering principles required to build production-grade AI systems.

These foundational patterns are the essential building blocks for the more advanced agentic systems we will explore. A solid understanding of how to structure and control the flow of information is the first step toward creating agents that can reason, plan, and take action.

Now that we have the workflow structures in place, the next logical step is to give them capabilities. In the next lesson, we will dive into Agent Tools and Function Calling, teaching you how to empower your LLM workflows to interact with external systems and perform actions in the real world.

## References

- [[1]](https://arxiv.org/pdf/2309.08181) [Using Large Language Models for Failure Mode and Effects Analysis](https://arxiv.org/pdf/2309.08181)
- [[2]](https://arxiv.org/html/2410.23884v1) [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/html/2410.23884v1)
- [[3]](https://www.getambassador.io/blog/prompt-engineering-for-llms) [Prompt Engineering for LLMs: A Practical Guide](https://www.getambassador.io/blog/prompt-engineering-for-llms)
- [[4]](https://dev.to/kapusto/enhancing-large-language-model-performance-with-prompt-chaining-2p84) [Enhancing Large Language Model Performance with Prompt Chaining](https://dev.to/kapusto/enhancing-large-language-model-performance-with-prompt-chaining-2p84)
- [[5]](https://www.vellum.ai/blog/what-is-prompt-chaining) [What is Prompt Chaining?](https://www.vellum.ai/blog/what-is-prompt-chaining)
- [[6]](https://blog.promptlayer.com/what-is-prompt-chaining/) [What is Prompt Chaining?](https://blog.promptlayer.com/what-is-prompt-chaining/)
- [[7]](https://www.voiceflow.com/blog/prompt-chaining) [Prompt Chaining: The Secret to Unlocking Complex LLM Use Cases](https://www.voiceflow.com/blog/prompt-chaining)
- [[8]](https://aisdr.com/blog/what-is-prompt-chaining/) [What is Prompt Chaining?](https://aisdr.com/blog/what-is-prompt-chaining/)
- [[9]](https://blog.promptlayer.com/what-is-prompt-chaining/) [What is Prompt Chaining?](https://blog.promptlayer.com/what-is-prompt-chaining/)
- [[10]](https://ai.plainenglish.io/prompt-chaining-is-dead-long-live-prompt-stuffing-58a1c08820c5) [Prompt Chaining is Dead. Long Live Prompt Stuffing.](https://ai.plainenglish.io/prompt-chaining-is-dead-long-live-prompt-stuffing-58a1c08820c5)
- [[11]](https://www.humanfirst.ai/blog/prompt-chaining) [Prompt Chaining: The Essential Technique for Complex LLM Applications](https://www.humanfirst.ai/blog/prompt-chaining)
- [[12]](https://platform.openai.com/docs/guides/rate-limits) [Rate limits](https://platform.openai.com/docs/guides/rate-limits)
- [[13]](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas) [Generative AI on Vertex AI quotas and limits](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas)
- [[14]](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits) [Azure OpenAI Service quotas and limits](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits)
- [[15]](https://docs.anthropic.com/en/docs/build-with-claude/rate-limits) [Rate limits](https://docs.anthropic.com/en/docs/build-with-claude/rate-limits)
- [[16]](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-routing.html) [Workflow for routing](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-routing.html)
- [[17]](https://arize.com/docs/phoenix/learn) [Workflows and Agents](https://arize.com/docs/phoenix/learn)
- [[18]](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns) [Spring AI Agentic Patterns](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns)
- [[19]](https://mikulskibartosz.name/ai-workflow-design-patterns) [AI Workflow Design Patterns](https://mikulskibartosz.name/ai-workflow-design-patterns)
- [[20]](https://arxiv.org/html/2402.02136v2) [A Comprehensive Taxonomy of User Intent in Large Language Models](https://arxiv.org/html/2402.02136v2)
- [[21]](https://rasa.com/docs/rasa/next/llms/llm-intent/) [LLM-based Intent Classification](https://rasa.com/docs/rasa/next/llms/llm-intent/)
- [[22]](https://spotintelligence.com/2023/11/03/intent-classification-nlp/) [Intent Classification in NLP](https://spotintelligence.com/2023/11/03/intent-classification-nlp/)
- [[23]](https://www.voiceflow.com/pathways/5-tips-to-optimize-your-llm-intent-classification-prompts) [5 Tips to Optimize Your LLM Intent Classification Prompts](https://www.voiceflow.com/pathways/5-tips-to-optimize-your-llm-intent-classification-prompts)
- [[24]](https://www.requesty.ai/blog/intelligent-llm-routing-in-enterprise-ai-uptime-cost-efficiency-and-model) [Intelligent LLM Routing in Enterprise AI](https://www.requesty.ai/blog/intelligent-llm-routing-in-enterprise-ai-uptime-cost-efficiency-and-model)
- [[25]](https://www.anthropic.com/research/building-effective-agents) [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [[26]](https://huggingface.co/blog/dcarpintero/design-patterns-for-building-agentic-workflows) [Design Patterns for Building Agentic Workflows](https://huggingface.co/blog/dcarpintero/design-patterns-for-building-agentic-workflows)
- [[27]](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-orchestration.html) [Workflow for orchestration](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-patterns/workflow-for-orchestration.html)
- [[28]](https://www.anthropic.com/research/building-effective-agents) [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [[29]](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns) [Spring AI Agentic Patterns](https://spring.io/blog/2025/01/21/spring-ai-agentic-patterns)
- [[30]](https://javaaidev.com/docs/agentic-patterns/patterns/orchestrator-workers-workflow/) [Orchestrator-Workers Workflow](https://javaaidev.com/docs/agentic-patterns/patterns/orchestrator-workers-workflow/)
- [[31]](https://bootcamptoprod.com/spring-ai-orchestrator-workers-workflow-guide/) [Spring AI Orchestrator-Workers Workflow Guide](https://bootcamptoprod.com/spring-ai-orchestrator-workers-workflow-guide/)

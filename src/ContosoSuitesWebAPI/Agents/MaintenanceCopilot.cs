// Exercise 5 Task 2 TODO #1: Add the library references to support Semantic Kernel, Chat Completion,
// and OpenAI Prompt Execution settings declarations.
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.ChatCompletion;

namespace ContosoSuitesWebAPI.Agents
{
    // Exercise 5 Task 2 TODO #2: Inject the Kernel service into the MaintenanceCopilot class.
    /// <summary>
    /// The maintenance copilot agent for assisting with maintenance requests.
    /// </summary>
    public class MaintenanceCopilot (Kernel kernel)
    {
        // Exercise 5 Task 2 TODO #3: Uncomment the two lines below to declare the Kernel and ChatHistory objects.
        public readonly Kernel _kernel = kernel;
        private ChatHistory _history = new( """
 You are a friendly assistant who likes to follow the rules. You will complete required steps
 and request approval before taking any consequential actions, such as saving the request to the database.
 If the user doesn't provide enough information for you to complete a task, you will keep asking questions
 until you have enough information to complete the task. Once the request has been saved to the database,
 inform the user that hotel maintenance has been notified and will address the issue as soon as possible.
 """
);

        /// <summary>
        /// Chat with the maintenance copilot.
        /// </summary>
        public async Task<string> Chat(string userPrompt)
        {
            // Exercise 5 Task 2 TODO #4: Comment out or delete the throw exception line below,
            // and then uncomment the remaining code in the function.
            // throw new NotImplementedException();

            var chatCompletionService = _kernel.GetRequiredService<IChatCompletionService>();

            var openAIPromptExecutionSettings = new OpenAIPromptExecutionSettings()
            {
               ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions
            };

            _history.AddUserMessage(userPrompt);

            var result = await chatCompletionService.GetChatMessageContentAsync(
               _history,
               executionSettings: openAIPromptExecutionSettings,
               _kernel
            );

            _history.AddAssistantMessage(result.Content!);

            return result.Content!;
        }
    }
}

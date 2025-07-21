using Amazon.Lambda.Core;
using Amazon.Lambda.RuntimeSupport;
using Amazon.Lambda.Serialization.SystemTextJson;
using System.Text.Json;

namespace eTendersLambda;
public class Function
{
    private static readonly HttpClient _httpClient = new HttpClient(); // Reusable HTTP client for API calls

    // This sets up the Lambda runtime, same as your original but with our async handler.
    public static async Task Main()
    {
        // Wraps our async handler
        Func<string, ILambdaContext, Task<string>> handler = FunctionHandler;
        await LambdaBootstrapBuilder.Create(handler, new DefaultLambdaJsonSerializer())
            .Build()
            .RunAsync();
    }

    // The function handler: Takes a string input (e.g., "2024-01-01" as dateFrom) and returns a string result.
    // We've made it async because API calls are async (like in Azure Functions).
    public static async Task<string> FunctionHandler(string dateFromInput, ILambdaContext context)
    {
        context.Logger.LogInformation($"Starting API fetch with dateFrom: {dateFromInput}");

        // Parse the input dateFrom (assume it's in YYYY-MM-DD format)
        if (!DateTime.TryParse(dateFromInput, out DateTime dateFrom))
        {
            context.Logger.LogError("Invalid dateFrom format. Use YYYY-MM-DD.");
            return "Error: Invalid dateFrom";
        }

        // Calculate dateTo: Exactly 1 year ahead
        DateTime dateTo = dateFrom.AddYears(1);

        // API settings
        const int pageSize = 50; // Fixed as per your endpoint
        int pageNumber = 1; // Start at page 1
        bool hasMorePages = true; // Loop control

        while (hasMorePages)
        {
            // Build the URL dynamically
            string url = $"https://ocds-api.etenders.gov.za/api/OCDSReleases?PageNumber={pageNumber}&PageSize={pageSize}&dateFrom={dateFrom:yyyy-MM-dd}&dateTo={dateTo:yyyy-MM-dd}";

            context.Logger.LogInformation($"Fetching page {pageNumber} from URL: {url}");

            // Call the API
            HttpResponseMessage response = await _httpClient.GetAsync(url);
            if (!response.IsSuccessStatusCode)
            {
                context.Logger.LogError($"API error: {response.StatusCode}");
                return $"Error: API call failed on page {pageNumber}";
            }

            // Read the JSON response as a string
            string json = await response.Content.ReadAsStringAsync();

            // TODO: Deserialize into your custom classes here.
            // For example (once you provide models):
            // var deserialized = JsonSerializer.Deserialize<YourRootModel>(json);
            // Then save to DB or process deserialized.Releases...

            // For now, log the raw JSON (or a placeholder object)
            var apiResponse = new ApiResponse { RawJson = json };
            context.Logger.LogInformation($"Page {pageNumber} response: {JsonSerializer.Serialize(apiResponse)}");

            // Check if there are more pages: If the JSON array length < pageSize, we're done.
            // This is a simple check assuming the API returns an array of results.
            // Adjust based on actual JSON structure (e.g., check "releases" array length).
            // For now, we'll simulate by checking if the JSON is empty or small.
            hasMorePages = !string.IsNullOrEmpty(json) && json.Length > 100; // Placeholder - improve this later
            // Better way (once models are ready): if (deserialized.Releases.Count == pageSize) hasMorePages = true;

            pageNumber++; // Move to next page
        }

        context.Logger.LogInformation("API fetch complete.");
        return "Done"; // Return a simple string (Lambda must return something)
    }
}

// We'll use this as a placeholder for your API response structure.
// Replace this with your actual classes later (e.g., a root object with lists of tenders).
// For now, it just holds the raw JSON as a string.
public class ApiResponse
{
    public string RawJson { get; set; } // Placeholder - we'll deserialize properly later
}
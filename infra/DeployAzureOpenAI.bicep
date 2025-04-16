@description('Location of the resources')
param location string = resourceGroup().location

var deployments = [
  {
    name: 'gpt-4o'
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
    sku: {
      name: 'GlobalStandard'
      capacity: 40
    }
  }
  {
    name: 'text-embedding-ada-002'
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    capacity: 120
  }
]

var openAIName = '${uniqueString(resourceGroup().id)}-openai'

@description('Creates an Azure OpenAI resource.')
module openAI 'core/ai/cognitiveservices.bicep' = {
  name: openAIName
  params: {
    location: location
    name: openAIName
    deployments: deployments
  }
}

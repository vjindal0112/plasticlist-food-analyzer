import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';

let client: ApolloClient<any> | null = null;

export function getApolloClient() {
  if (typeof window === 'undefined') {
    return null;
  }
  if (!client) {
    client = new ApolloClient({
      link: new HttpLink({
        uri: 'http://localhost:8000/graphql', // Your GraphQL endpoint
      }),
      cache: new InMemoryCache(),
    });
  }
  return client;
}
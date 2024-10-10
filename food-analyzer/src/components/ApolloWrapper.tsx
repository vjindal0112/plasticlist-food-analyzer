'use client';

import { ApolloProvider } from '@apollo/client';
import { getApolloClient } from '@/lib/apollo-client';

export function ApolloWrapper({ children }: { children: React.ReactNode }) {
  const client = getApolloClient();

  if (!client) {
    return <>{children}</>;
  }

  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
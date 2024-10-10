'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { ApolloProvider } from '@apollo/client';
import { client } from '@/lib/apollo-client';
import 'graphiql/graphiql.min.css';

const GraphiQL = dynamic(
  () => import('graphiql').then((mod) => mod.GraphiQL),
  { ssr: false }
);

function GraphiQLPage() {
  const fetcher = async (params: any) => {
    const response = await fetch('http://localhost:8000/graphql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    return response.json();
  };

  return (
    <ApolloProvider client={client}>
      <div style={{ height: '100vh' }}>
        <GraphiQL fetcher={fetcher} />
      </div>
    </ApolloProvider>
  );
}

export default GraphiQLPage;
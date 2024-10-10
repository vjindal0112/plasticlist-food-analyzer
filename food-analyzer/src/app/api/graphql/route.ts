import { createYoga } from 'graphql-yoga'
import { NextResponse } from 'next/server'
import { schema } from '@/lib/schema'  // You'll need to create this

const { handleRequest } = createYoga({
  schema,
  graphqlEndpoint: '/api/graphql',
  fetchAPI: { Request, Response: NextResponse }
})

export { handleRequest as GET, handleRequest as POST }
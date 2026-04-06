import { Environment, Network, RecordSource, Store, FetchFunction } from 'relay-runtime';

const fetchFn: FetchFunction = async (request, variables) => {
  const response = await fetch('/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: request.text, variables }),
  });
  if (!response.ok) {
    throw new Error(`GraphQL request failed: ${response.status}`);
  }
  return response.json();
};

const environment = new Environment({
  network: Network.create(fetchFn),
  store: new Store(new RecordSource()),
  getDataID: (fieldValue, typeName) =>
    fieldValue.id != null ? `${typeName}:${fieldValue.id}` : undefined,
});

export default environment;

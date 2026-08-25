// Compatibility shim for the unchanged Dashboard.vue import
// The supplied API contract contains no paddocks/livestock/tasks/weather/alerts
// endpoints, so this helper never invents or discovers undocumented routes
export async function getResource(resource) {
  throw new Error(`No documented API endpoint exists for resource: ${resource}.`);
}

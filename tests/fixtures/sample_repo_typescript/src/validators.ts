export function requireId(id: string): void {
  if (!id) throw new Error('id is required');
}

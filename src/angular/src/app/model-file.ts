/**
 * Model file received from the backend
 * Note: Naming convention matches that used in the JSON
 */
export interface ModelFile {
    name: string;
    local_size: number;
    remote_size: number;
}

/**
 * Class representing a worker for uploading blobs.
 */
class BlobUploadWorker {
  /** @type number The unique identifier for the worker. */
  id;

  /** @type {BlobUploadTask[]} The list of tasks assigned to the worker. */
  tasks;

  /**
   * Creates an instance of BlobUploadWorker.
   * @param {number} workerId - The unique identifier for the worker.
   * @param {BlobUploadTask[]} tasks - The tasks to be executed by the worker.
   */
  constructor(workerId, tasks) {
    this.id = workerId;
    this.tasks = tasks;
  }

  /**
   * Starts the upload tasks for the worker.
   * @returns Promise<void> - A promise that resolves when all tasks are completed.
   */
  start = async () => {
    while (this.tasks.length > 0) {
      const task = this.tasks.shift();
      await task.run();

      // Low random delay to avoid freezing the UI
      await new Promise((r) => setTimeout(r, Math.random() * 10));
    }
  };
}

export { BlobUploadWorker };

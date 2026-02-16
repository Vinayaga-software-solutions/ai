<?php

namespace App\Services;

use App\Models\DataFile;
use Google\Cloud\PubSub\PubSubClient;
use Illuminate\Support\Facades\Log;
use Throwable;

class DataFilePubSubPublisher
{
    public function publishFileUploaded(DataFile $dataFile): void
    {
        $projectId = (string) config('services.gcp_pubsub.project_id', '');
        $topicName = (string) config('services.gcp_pubsub.topic', '');
        $keyFilePath = (string) config('services.gcp_pubsub.key_file_path', '');

        if ($projectId === '' || $topicName === '') {
            Log::warning('Pub/Sub publish skipped: missing project/topic config.', [
                'data_file_id' => $dataFile->id,
            ]);
            return;
        }

        try {
            $clientConfig = ['projectId' => $projectId];
            if ($keyFilePath !== '') {
                $clientConfig['keyFilePath'] = $keyFilePath;
            }

            $pubSub = new PubSubClient($clientConfig);
            $topic = $pubSub->topic($topicName);

            $payload = $this->buildPayload($dataFile);

            $topic->publish([
                'data' => json_encode($payload, JSON_UNESCAPED_SLASHES),
                'attributes' => [
                    'event_type' => 'data_file_uploaded',
                    'data_id' => (string) $dataFile->data_id,
                    'data_file_id' => (string) $dataFile->id,
                ],
            ]);
        } catch (Throwable $e) {
            Log::error('Failed to publish file upload event to Pub/Sub.', [
                'data_file_id' => $dataFile->id,
                'error' => $e->getMessage(),
            ]);
        }
    }

    private function buildPayload(DataFile $dataFile): array
    {
        $data = $dataFile->data()->with('dataCollection.project')->first();
        $collection = $data?->dataCollection;
        $project = $collection?->project;
        $bucket = (string) config('filesystems.disks.gcs.bucket', '');

        return [
            'event_type' => 'data_file_uploaded',
            'occurred_at' => now()->toIso8601String(),
            'data_file' => [
                'id' => $dataFile->id,
                'data_id' => $dataFile->data_id,
                'original_name' => $dataFile->original_name,
                'storage_path' => $dataFile->storage_path,
                'mime_type' => $dataFile->mime_type,
                'size' => $dataFile->size,
                'created_at' => optional($dataFile->created_at)?->toIso8601String(),
            ],
            'data' => [
                'id' => $data?->id,
                'name' => $data?->name,
                'type' => $data?->type,
                'storage_path' => $data?->storage_path,
                'data_collection_id' => $data?->data_collection_id,
                'created_by' => $data?->created_by,
            ],
            'data_collection' => [
                'id' => $collection?->id,
                'name' => $collection?->name,
                'project_id' => $collection?->project_id,
            ],
            'project' => [
                'id' => $project?->id,
                'name' => $project?->name,
            ],
            'storage' => [
                'disk' => config('filesystems.default'),
                'bucket' => $bucket,
                'gcs_uri' => $bucket !== '' ? "gs://{$bucket}/{$dataFile->storage_path}" : null,
            ],
        ];
    }
}


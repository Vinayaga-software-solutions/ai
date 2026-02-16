<?php

namespace App\Http\Controllers;

use App\Models\Data;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\Http\UploadedFile;

class DataFileUploadController extends Controller
{
    public function store(Request $request, Data $data): JsonResponse
    {
        Gate::authorize('update', $data);

        if ($data->type !== 'document') {
            return response()->json([
                'message' => 'Files can only be uploaded for document type data sources.',
            ], 422);
        }

        $uploadedFiles = $this->extractUploadedFiles($request);

        if (count($uploadedFiles) === 0) {
            return response()->json([
                'message' => 'The file field is required.',
                'errors' => [
                    'file' => ['No uploaded file was found. Send multipart/form-data with a file field.'],
                ],
            ], 422);
        }

        validator(
            ['files' => $uploadedFiles],
            ['files' => ['required', 'array', 'min:1'], 'files.*' => ['file', 'mimes:pdf,txt,doc,docx,md', 'max:10240']]
        )->validate();

        $createdFiles = [];
        foreach ($uploadedFiles as $uploadedFile) {
            $path = $uploadedFile->store($data->storage_path, config('filesystems.default'));

            $createdFiles[] = $data->files()->create([
                'original_name' => $uploadedFile->getClientOriginalName(),
                'storage_path' => $path,
                'mime_type' => $uploadedFile->getMimeType(),
                'size' => $uploadedFile->getSize(),
            ]);
        }

        return response()->json([
            'message' => count($createdFiles).' file(s) added successfully.',
            'count' => count($createdFiles),
            'data_files' => array_map(function ($dataFile) {
                return [
                    'id' => $dataFile->id,
                    'data_id' => $dataFile->data_id,
                    'original_name' => $dataFile->original_name,
                    'storage_path' => $dataFile->storage_path,
                    'mime_type' => $dataFile->mime_type,
                    'size' => $dataFile->size,
                    'created_at' => $dataFile->created_at,
                ];
            }, $createdFiles),
        ], 200);
    }

    /**
     * Collect all uploaded files from multipart payload regardless of key shape.
     *
     * @return UploadedFile[]
     */
    private function extractUploadedFiles(Request $request): array
    {
        $files = [];

        foreach ($request->allFiles() as $file) {
            $this->flattenUploadedFiles($file, $files);
        }

        return $files;
    }

    /**
     * @param mixed $node
     * @param UploadedFile[] $files
     */
    private function flattenUploadedFiles(mixed $node, array &$files): void
    {
        if ($node instanceof UploadedFile) {
            $files[] = $node;
            return;
        }

        if (is_array($node)) {
            foreach ($node as $child) {
                $this->flattenUploadedFiles($child, $files);
            }
        }
    }
}

package main

deny contains msg if {
    resource := input.planned_values.root_module.resources[_]
    resource.type == "aws_s3_bucket_public_access_block"
    resource.values.block_public_acls == false
    msg := sprintf("DENIED: %s has block_public_acls disabled — S3 buckets must block public access.", [resource.address])
}

deny contains msg if {
    resource := input.planned_values.root_module.resources[_]
    resource.type == "aws_s3_bucket_public_access_block"
    resource.values.block_public_policy == false
    msg := sprintf("DENIED: %s has block_public_policy disabled — S3 buckets must block public access.", [resource.address])
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web_server" {
  name        = "web-server-sg"
  description = "Web server security group"

  # VIOLATION: SSH open to the internet — deny_open_ssh.rego will catch this
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # VIOLATION: RDP open to the internet — deny_open_rdp.rego will catch this
  ingress {
    description = "RDP"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-company-data-bucket"
}

# VIOLATION: Public access block disabled — deny_public_s3.rego will catch this
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

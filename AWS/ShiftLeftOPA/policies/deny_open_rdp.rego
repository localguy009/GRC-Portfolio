package main

deny contains msg if {
    resource := input.planned_values.root_module.resources[_]
    resource.type == "aws_security_group"
    ingress := resource.values.ingress[_]
    ingress.from_port <= 3389
    ingress.to_port >= 3389
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"
    msg := sprintf("DENIED: %s allows RDP (port 3389) from 0.0.0.0/0 — restrict to a known IP range.", [resource.address])
}

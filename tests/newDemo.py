#!/usr/bin/env python3
from palimpzest.elements import Schema, StringField
from palimpzest.policy import *

from tabulate import tabulate

import gradio as gr
import palimpzest as pz
import pandas as pd

import time


def emitNestedTuple(node, indent=0):
    elt, child = node
    print(" " * indent, elt)
    if child is not None:
        emitNestedTuple(child, indent=indent+2)

def printTable(records, cols=None, gradio=False):
    records = [
        {
            key: record.__dict__[key]
            for key in record.__dict__
            if not key.startswith('_')
        }
        for record in records
    ]
    records_df = pd.DataFrame(records)
    print_cols = records_df.columns if cols is None else cols

    if not gradio:
        print(tabulate(records_df[print_cols], headers="keys", tablefmt='psql'))

    else:
        with gr.Blocks() as demo:
            gr.Dataframe(records_df[print_cols])

        demo.launch()

# TODO: I want this to "just work" if it inherits from Schema instead of TextFile;
#       for some reason, inheriting from Schema leads to the "contents" being a bytes
#       field but if Email inherits from File or TextFile, it becomes a string;
#       this is important b/c dr.asTextJSON() will ignore bytes field(s).
class Email(pz.TextFile):
    """Represents an email, which in practice is usually from a text file"""
    sender = StringField(desc="The email address of the sender", required=True)
    subject = StringField(desc="The subject of the email", required=True)


if __name__ == "__main__":
    """
    This demo illustrates how the cost optimizer can produce and evaluate multiple plans.
    """
    # user implemented plan
    emails = pz.Dataset(source="enron-tiny", schema=Email)
    emails = emails.filterByStr("The email is about someone taking a vacation")
    emails = emails.filterByStr("The email is sent by Larry")

    # get logical tree
    logicalTree = emails.getLogicalTree()

    # get candidate physical plans
    candidatePlans = logicalTree.createPhysicalPlanCandidates()

    # use sampling to get better information about plans
    # sampler = SimpleSampler(min=10)
    # candidatePlans = logicalTree.createPhysicalPlanCandidates(sampler=sampler)

    # # print out plans to the user
    # print("----------")
    # for idx, cp in enumerate(candidatePlans):
    #     print(f"Plan {idx}: Time est: {cp[0]:.3f} -- Cost est: {cp[1]:.3f} -- Quality est: {cp[2]:.3f}")
    #     print("Physical operator tree")
    #     physicalOps = cp[3].dumpPhysicalTree()
    #     emitNestedTuple(physicalOps)
    #     print("----------")

    # have policy select the candidate plan to execute
    myPolicy = MinCost()
    planTime, planCost, quality, physicalTree = myPolicy.choose(candidatePlans)
    print("----------")
    print(f"Policy is: {str(myPolicy)}")
    print(f"Chose plan: Time est: {planTime:.3f} -- Cost est: {planCost:.3f} -- Quality est: {quality:.3f}")
    emitNestedTuple(physicalTree.dumpPhysicalTree())

    # execute the plan
    startTime = time.time()
    records = []
    for r in physicalTree:
        records.append(r)

    # pretty print a table of the output records
    print("----------")
    print()
    printTable(records, cols=["sender", "subject"], gradio=True)

    endTime = time.time()
    print("Elapsed time:", endTime - startTime)

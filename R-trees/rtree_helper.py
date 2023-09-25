import matplotlib.pyplot as plt
import matplotlib.patches as patches

max_hash_value=30
max_awards_value=30

def visualize_rtree(node, ax):
    if not node:
        return

    if node.leaf: 
        rect = node.mbr
        ax.add_patch(patches.Rectangle((rect.xmin, rect.ymin), rect.xmax-rect.xmin, rect.ymax-rect.ymin, fill=False))
    else:
        # Draw the MBRs in internal nodes
        for child_node in node.entries:
            rect = child_node.mbr  # Accessing the MBR of the child_node
            ax.add_patch(patches.Rectangle((rect.xmin, rect.ymin), rect.xmax-rect.xmin, rect.ymax-rect.ymin, fill=False, edgecolor='red', linestyle='--'))
            visualize_rtree(child_node, ax)  # Recursive call for child nodes


def plot_rtree(tree):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.autoscale_view()

    # Start the recursive visualization from the root
    visualize_rtree(tree.root, ax)

    ax.set_xlim([0, max_hash_value])  # Adjust these values as per your data range
    ax.set_ylim([0, max_awards_value])  # Adjust these values as per your data range

    plt.show()

def print_tree(node, level=0, prefix="Root: "):
    indent = '  ' * level

    # Print MBR of the node along with a prefix to identify the node type
    if node.mbr:
        print(f"{indent}{prefix}MBR: {node.mbr.xmin, node.mbr.ymin, node.mbr.xmax, node.mbr.ymax}")

    # If node has entries
    for i, entry in enumerate(node.entries):
        if node.leaf:
            # Print entry details
            print(f"{indent}  Entry {i+1}: ({entry.surname}, {entry.awards})")
        else:
            # Recursive call to print child nodes
            print_tree(entry, level+1, prefix=f"Child {i+1}: ")

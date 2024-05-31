import {GraphCanvas, GraphCanvasRef, LayoutTypes} from "reagraph"
import {AppBar, IconButton, Toolbar, Tooltip, Typography} from "@mui/material";
import "./style/app.sass"
import {NodeMenu} from "./NodeMenu.tsx";
import {NodeContextProvider, NodeType, PDDLGraphNode, useNodeContext} from "./NodeContext.tsx";
import {PlayArrow, Refresh, HourglassBottom, FastForward, Add} from "@mui/icons-material"
import {NodeModalContextProvider, useNodeModalContext} from "./NodeModal.tsx";
import {useEffect, useRef, useState} from "react";

const Content = () => {

    const nodeContext = useNodeContext()
    const nodeModalContext = useNodeModalContext()
    const graphRef = useRef() as any
    const graph = useRef<GraphCanvasRef|null>(null)
    const [layout, setLayout] = useState("forceDirected2d");

    useEffect(() => {
        if(nodeContext.selected)
            try {
                graph.current?.centerGraph([nodeContext.selected])
            } catch (e) {
                setTimeout(() => graph.current?.centerGraph([nodeContext.selected]), 500)
            }
    }, [nodeContext.selected]);

    useEffect(() => {
        setLayout(l => (l == "forceDirected2d" ? "forceDirected3d" : "forceDirected2d"))
    }, [nodeContext.nodes, nodeContext.edges]);

    return <>
        <AppBar position="fixed" sx={{zIndex: (theme) => theme.zIndex.drawer + 1}} className="navbar">
            <Toolbar>
                <Typography
                    variant="h6"
                    noWrap
                    component="a"
                    sx={{
                        mr: 2,
                        display: {xs: 'none', md: 'flex'},
                        fontFamily: 'monospace',
                        fontWeight: 700,
                        letterSpacing: '.3rem',
                        textDecoration: 'none',
                    }}
                >
                    AI-ROB
                </Typography>
                <div className="toolbar">
                    <Tooltip title={"Plan"}>
                        <span>
                            <IconButton
                                disabled={nodeContext.getSelected()?.type == NodeType.ACTION || !nodeContext.hasNext()}
                                style={{color: (nodeContext.getSelected()?.type != NodeType.ACTION && nodeContext.hasNext()) ? "#FFF" : "#AAA"}}
                                onClick={() => nodeContext.plan()}>
                                <HourglassBottom/>
                            </IconButton>
                        </span>
                    </Tooltip>
                    <Tooltip title={"Add Node"}>
                        <span>
                            <IconButton
                                style={{color: "#FFF"}}
                                onClick={() => nodeContext.add_new(null, {
                                    type: NodeType.WAYPOINT,
                                    label: "New State",
                                    predicates: []
                                })}>
                                <Add/>
                            </IconButton>
                        </span>
                    </Tooltip>
                    <Tooltip title={"Single Step"}>
                        <span>
                            <IconButton disabled={!nodeContext.hasNext()}
                                        style={{color: nodeContext.hasNext() ? "#FFF" : "#AAA"}} onClick={() => {
                                nodeContext.execute(true)
                            }}>
                                <PlayArrow/>
                            </IconButton>
                        </span>
                    </Tooltip>
                    <Tooltip title={"Execute"}>
                        <span>
                            <IconButton disabled={!nodeContext.hasNext()}
                                        style={{color: nodeContext.hasNext() ? "#FFF" : "#AAA"}} onClick={async () => {
                                nodeContext.execute(false)
                            }}>
                                <FastForward/>
                            </IconButton>
                        </span>
                    </Tooltip>
                    <Tooltip title={"Reset"}>
                        <span>
                            <IconButton style={{color: "#FFF"}} onClick={() => {
                                if (confirm("Everything will be lost, even your mental sanity. Are you sure to continue?"))
                                    nodeContext.reset()
                            }}>
                                <Refresh/>
                            </IconButton>
                        </span>
                    </Tooltip>
                </div>
            </Toolbar>
        </AppBar>
        <div ref={graphRef} className="graph" style={{position: 'relative'}}>
            <GraphCanvas
                nodes={nodeContext.nodes}
                edges={nodeContext.edges}
                ref={graph}
                layoutType={layout as LayoutTypes}
                contextMenu={({data, onClose}) =>
                    <NodeMenu nodeContext={nodeContext} nodeModalContext={nodeModalContext}
                              node={data as unknown as PDDLGraphNode} onClose={onClose} graphContainerRef={graphRef}/>}
                onNodeDoubleClick={(node) => {
                    if (node.id !== "Initial State")
                        nodeModalContext.show(node.id)
                }}
                draggable
            />
        </div>
    </>
}

function App() {


    return (
        <NodeContextProvider>
            <NodeModalContextProvider>
                <Content/>
            </NodeModalContextProvider>
        </NodeContextProvider>
    )
}

export default App

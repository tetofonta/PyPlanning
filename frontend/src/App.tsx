import {GraphCanvas, recommendLayout} from "reagraph"
import {AppBar, IconButton, Toolbar, Typography} from "@mui/material";
import "./style/app.sass"
import {NodeMenu} from "./NodeMenu.tsx";
import {NodeContextProvider, NodeType, PDDLGraphNode, useNodeContext} from "./NodeContext.tsx";
import {PlayArrow, Refresh, HourglassBottom, FastForward} from "@mui/icons-material"
import {NodeModalContextProvider, useNodeModalContext} from "./NodeModal.tsx";
import {useRef} from "react";

const Content = () => {

    const nodeContext = useNodeContext()
    const nodeModalContext = useNodeModalContext()
    const graphRef = useRef() as any
    // const layout = recommendLayout(nodeContext.nodes, nodeContext.edges);

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
                    <IconButton disabled={nodeContext.getSelected()?.type == NodeType.ACTION || !nodeContext.hasNext()}
                                style={{color: (nodeContext.getSelected()?.type != NodeType.ACTION && nodeContext.hasNext()) ? "#FFF" : "#AAA"}} onClick={() => {
                        //plan and insert new action nodes if we are not in an action node.
                        fetch("/api/plan", {
                            method: 'POST',
                            headers: {'Content-Type': "application/json"},
                            body: JSON.stringify(nodeContext.getNextWaypoint()?.predicates)
                        }).then(res => res.json())
                        .then(data => {
                            data.reverse().forEach((e: any) => nodeContext.append_new({
                                type: NodeType.ACTION,
                                predicates: [],
                                selected: false,
                                label: `${e.action}(${e.params.join(", ")})`
                            }))
                        }).then(() => {
                            // setTimeout(() => nodeContext.next(), 1000) TODO
                        }).catch(() => {
                        })
                    }}>
                        <HourglassBottom/>
                    </IconButton>
                    <IconButton disabled={!nodeContext.hasNext()}
                                style={{color: nodeContext.hasNext() ? "#FFF" : "#AAA"}} onClick={() => {
                        nodeContext.next()
                    }}>
                        <PlayArrow/>
                    </IconButton>
                    {/*<IconButton disabled={!nodeContext.hasNext()}*/}
                    {/*            style={{color: nodeContext.hasNext() ? "#FFF" : "#AAA"}} onClick={async () => {*/}
                    {/*                while (nodeContext.getSelected()?.child != nodeContext.getNextWaypoint()) {*/}
                    {/*                    nodeContext.next()*/}
                    {/*                    await new Promise<void>(res => setTimeout(() => res(), 500))*/}
                    {/*                }*/}
                    {/*}}>*/}
                    {/*    <FastForward/>*/}
                    {/*</IconButton>*/}
                    <IconButton style={{color: "#FFF"}} onClick={() => {
                        if (confirm("Everything will be lost, even your mental sanity. Are you sure to continue?"))
                            nodeContext.reset()
                    }}>
                        <Refresh/>
                    </IconButton>
                </div>
            </Toolbar>
        </AppBar>
        <div ref={graphRef} className="graph" style={{position: 'relative'}}>
            <GraphCanvas
                nodes={nodeContext.nodes}
                edges={nodeContext.edges}
                layoutType={"treeLr2d"}
                contextMenu={({data, onClose}) =>
                    <NodeMenu nodeContext={nodeContext} nodeModalContext={nodeModalContext}
                              node={data as unknown as PDDLGraphNode} onClose={onClose} graphContainerRef={graphRef}/>}
                onNodeDoubleClick={(node) => {
                    if (node.id != "Initial State")
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
